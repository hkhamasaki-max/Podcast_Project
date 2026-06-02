# Program Card Viewer - Streamlit + Google Sheets

Google Sheetsをデータベースとして使うカード表示アプリです。`favorite` と `user_note` はGoogle Sheetsへ保存されます。xlsxをアップロードしてGoogle Sheetsへ反映することもできます。

初心者向けの詳しい手順は `SETUP_GUIDE_JA.md` を見てください。

## 使うサービス

- Streamlit Community Cloud: アプリを公開する場所
- Google Sheets: データベース
- Google Cloudのサービスアカウント: StreamlitからGoogle Sheetsを読み書きするための鍵

## データ準備

1. `Program_List.xlsx` をGoogle Sheetsで開く、またはGoogle Sheetsへインポートします。
2. `favorite` 列がなければ追加します。
3. `user_note` 列がなければ追加します。
4. Google SheetsのURLからスプレッドシートIDを控えます。

URL例:

```text
https://docs.google.com/spreadsheets/d/ここがspreadsheet_id/edit
```

## Google Cloud側の準備

1. Google Cloudでプロジェクトを作成します。
2. Google Sheets APIを有効化します。
3. サービスアカウントを作成します。
4. サービスアカウントのJSONキーを作成します。
5. Google Sheetsの共有ボタンから、サービスアカウントのメールアドレスに編集権限を付けます。

サービスアカウントのメールアドレスはJSONキー内の `client_email` です。

## Streamlit secrets

`secrets_template.toml` を参考に、Streamlit Community CloudのSecretsへ設定します。

`.streamlit/secrets.example.toml` も同じ内容ですが、先頭にドットがある `.streamlit` フォルダはFinderで見えにくいことがあります。

ローカルで動かす場合は、同じ内容を `.streamlit/secrets.toml` として保存します。

## Streamlit Community Cloudへの公開

1. このフォルダの中身をGitHubリポジトリへ置きます。
2. Streamlit Community CloudでCreate appを選びます。
3. entrypoint fileに `app.py` を指定します。
4. SecretsにGoogle Sheetsとサービスアカウント情報を貼り付けます。
5. Deployします。

## ローカル起動

```bash
python -m streamlit run app.py
```

## スマホで使う

Streamlit Community Cloudで発行されたURLをスマホで開きます。編集するとGoogle Sheetsへ保存されます。

## 注意

Google Sheetsをデータベースとして使うため、同時に複数人が同じ行を編集すると後から保存した内容が反映されます。最初は個人利用や少人数利用に向いています。
