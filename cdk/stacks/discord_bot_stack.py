from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    aws_lambda as lambda_,
    aws_apigatewayv2 as apigateway,
    aws_apigatewayv2_integrations as integrations,
    aws_sqs as sqs,
    aws_lambda_event_sources as event_sources,
    aws_logs as logs,
    aws_iam as iam,
    aws_ssm as ssm,
)
from constructs import Construct
from aws_cdk.aws_lambda_python_alpha import PythonFunction


class DiscordBotStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # SQS Queue for async processing
        audio_processing_queue = sqs.Queue(
            self,
            "AudioProcessingQueue",
            visibility_timeout=Duration.minutes(15),
            retention_period=Duration.days(1),
        )

        # Lambda Layer for dependencies
        dependencies_layer = lambda_.LayerVersion(
            self,
            "DependenciesLayer",
            code=lambda_.Code.from_asset("layers/dependencies"),
            compatible_runtimes=[
                lambda_.Runtime.PYTHON_3_11,
            ],
            description="Discord bot dependencies",
        )

        # Environment variables from SSM Parameter Store
        discord_token_param = ssm.StringParameter.from_secure_string_parameter_attributes(
            self,
            "DiscordToken",
            parameter_name="/discord-bot/discord-token",
        )

        openai_api_key_param = ssm.StringParameter.from_secure_string_parameter_attributes(
            self,
            "OpenAIApiKey",
            parameter_name="/discord-bot/openai-api-key",
        )

        # Common Lambda environment
        common_env = {
            "QUEUE_URL": audio_processing_queue.queue_url,
            "LOG_LEVEL": "INFO",
            "MAX_AUDIO_SIZE_MB": "25",
            "MAX_DURATION_SECONDS": "600",
            "DAILY_COST_LIMIT_USD": "10.0",
        }

        # Discord interaction handler (fast response)
        interaction_handler = PythonFunction(
            self,
            "InteractionHandler",
            entry="src",
            index="lambda_handlers/interaction_handler.py",
            handler="handler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            timeout=Duration.seconds(10),
            memory_size=256,
            environment={
                **common_env,
                "DISCORD_TOKEN": discord_token_param.string_value,
            },
            layers=[dependencies_layer],
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Grant permissions to read SSM parameters
        discord_token_param.grant_read(interaction_handler)

        # Grant permission to send messages to SQS
        audio_processing_queue.grant_send_messages(interaction_handler)

        # Audio processing handler (async)
        processing_handler = PythonFunction(
            self,
            "ProcessingHandler",
            entry="src",
            index="lambda_handlers/processing_handler.py",
            handler="handler",
            runtime=lambda_.Runtime.PYTHON_3_11,
            timeout=Duration.minutes(15),
            memory_size=1024,
            ephemeral_storage_size=10240,  # 10GB
            environment={
                **common_env,
                "DISCORD_TOKEN": discord_token_param.string_value,
                "OPENAI_API_KEY": openai_api_key_param.string_value,
            },
            layers=[dependencies_layer],
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # Grant permissions to read SSM parameters
        discord_token_param.grant_read(processing_handler)
        openai_api_key_param.grant_read(processing_handler)

        # Add SQS event source
        processing_handler.add_event_source(
            event_sources.SqsEventSource(
                audio_processing_queue,
                batch_size=1,
                max_batching_window_duration=Duration.seconds(5),
            )
        )

        # API Gateway for Discord webhook
        api = apigateway.HttpApi(
            self,
            "DiscordBotApi",
            cors_preflight=apigateway.CorsPreflightOptions(
                allow_origins=["https://discord.com"],
                allow_methods=[apigateway.CorsHttpMethod.POST],
            ),
        )

        # Add route
        api.add_routes(
            path="/discord/interactions",
            methods=[apigateway.HttpMethod.POST],
            integration=integrations.HttpLambdaIntegration(
                "InteractionIntegration",
                interaction_handler,
            ),
        )

        # Output the API endpoint
        self.api_url = api.url
        if self.api_url:
            ssm.StringParameter(
                self,
                "ApiEndpointParameter",
                parameter_name="/discord-bot/api-endpoint",
                string_value=f"{self.api_url}discord/interactions",
            )
