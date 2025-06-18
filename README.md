# Discord Voice Message Transcription Bot

Discord の音声メッセージを自動で文字起こしする Bot です。OpenAI Whisper API を使用し、AWS Lambda 上で動作します。

## 🎯 特徴

- Discord の音声メッセージを自動検出
- OpenAI Whisper API による高精度な日本語文字起こし
- AWS Lambda によるサーバーレス構成
- コスト効率的な運用（月額約 $15）

## 🛠️ 技術スタック

- **言語**: Python 3.11
- **Discord ライブラリ**: discord.py 2.5+
- **音声認識**: OpenAI Whisper API
- **インフラ**: AWS Lambda + API Gateway
- **パッケージ管理**: uv

## 📋 必要な環境

- Python 3.11+
- AWS アカウント
- Discord Developer アカウント
- OpenAI API キー

## 🚀 セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/tqer39/discord-voice-message-transcription-bot.git
cd discord-voice-message-transcription-bot
```

### 2. 依存関係のインストール

```bash
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example` を `.env` にコピーして編集：

```bash
cp .env.example .env
```

必要な環境変数：
- `DISCORD_TOKEN`: Discord Bot のトークン
- `OPENAI_API_KEY`: OpenAI API キー
- `AWS_REGION`: AWS リージョン（例: ap-northeast-1）

### 4. Discord Bot の作成

1. [Discord Developer Portal](https://discord.com/developers/applications) で新しいアプリケーションを作成
2. Bot セクションでトークンを取得
3. 必要な権限を設定（Send Messages, Read Message History, Attach Files）

### 5. AWS へのデプロイ

```bash
# SAM CLI を使用してデプロイ
sam build
sam deploy --guided
```

## 🎮 使い方

1. Bot を Discord サーバーに招待
2. 音声メッセージを送信
3. Bot が自動的に文字起こし結果を返信

## 📂 プロジェクト構造

```
discord-voice-message-transcription-bot/
├── src/
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── discord_bot.py
│   │   └── handlers.py
│   ├── transcription/
│   │   ├── __init__.py
│   │   └── whisper_client.py
│   └── lambda_handler.py
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── samconfig.toml
└── template.yaml
```

## 💰 コスト見積もり

1日100回の使用を想定：
- OpenAI Whisper API: 約 $13.50/月
- AWS Lambda + API Gateway: 約 $1-2/月
- **合計: 約 $15/月**

## 🤝 コントリビューション

Issue や Pull Request を歓迎します！

## 📄 ライセンス

MIT License

## 👤 作者

- **Takeru O'oyama** - [@tqer39](https://github.com/tqer39)

## 🔗 関連リンク

- [Discord Developer Documentation](https://discord.com/developers/docs)
- [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
