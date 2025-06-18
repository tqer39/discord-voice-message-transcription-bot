#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from cdk.stacks.discord_bot_stack import DiscordBotStack

app = App()

# 環境設定
env = Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION", "ap-northeast-1"),
)

# スタックの作成
DiscordBotStack(
    app,
    "DiscordVoiceTranscriptionBotStack",
    env=env,
    description="Discord voice message transcription bot infrastructure",
)

app.synth()
