# はじめての公開手順

このアプリは、次の3つをつなげて使います。

```text
スマホ/PCブラウザ
  ↓
Streamlitのアプリ画面
  ↓
Google Sheetsのデータ
```

GitHubは、Streamlitにアプリのファイルを渡すための置き場所です。

## まず用意するもの

- Googleアカウント
- GitHubアカウント
- Streamlitアカウント
- `Program_List.xlsx`

## 手順1: xlsxをGoogle Sheetsにする

1. Google Driveを開きます。
2. `Program_List.xlsx` をアップロードします。
3. アップロードしたファイルを右クリックします。
4. 「アプリで開く」からGoogle Sheetsで開きます。
5. Google Sheetsとして保存されていることを確認します。
6. 1行目に `favorite` と `user_note` の列があるか確認します。

`favorite` はTRUE/FALSEを入れる列です。  
`user_note` は自由メモを入れる列です。

## 手順2: スプレッドシートIDを控える

Google SheetsのURLは次のような形です。

```text
https://docs.google.com/spreadsheets/d/長いID/edit
```

`/d/` と `/edit` の間が `spreadsheet_id` です。

## 手順3: Google Cloudで鍵を作る

ここが一番つまずきやすい場所です。

1. Google Cloud Consoleを開きます。
2. 新しいプロジェクトを作ります。
3. 「APIとサービス」へ進みます。
4. 「ライブラリ」からGoogle Sheets APIを検索します。
5. Google Sheets APIを有効にします。
6. 「認証情報」へ進みます。
7. 「認証情報を作成」から「サービスアカウント」を選びます。
8. サービスアカウントを作成します。
9. 作成したサービスアカウントを開きます。
10. 「キー」タブでJSONキーを作成します。
11. ダウンロードされたJSONファイルを保管します。

JSONファイルの中にある `client_email` が重要です。

## 手順4: Google Sheetsをサービスアカウントに共有する

1. Google Sheetsを開きます。
2. 右上の「共有」を押します。
3. JSON内の `client_email` を入力します。
4. 権限を「編集者」にします。
5. 共有します。

これをしないと、StreamlitからGoogle Sheetsを読めません。

## 手順5: GitHubにアプリを置く

1. GitHubで新しいリポジトリを作ります。
2. `app.py` と `requirements.txt` をアップロードします。
3. `secrets_template.toml` はアップロードしてもしなくても大丈夫です。

本物の秘密鍵はGitHubに置かないでください。

## 手順6: Streamlitでアプリを作る

1. Streamlit Community Cloudを開きます。
2. 「Create app」または「New app」を押します。
3. GitHubのリポジトリを選びます。
4. Branchは通常 `main` を選びます。
5. Main file pathは `app.py` にします。
6. Advanced settingsを開きます。
7. Secrets欄に設定を貼り付けます。
8. Deployします。

## 手順7: Secretsに貼る内容を作る

`secrets_template.toml` を開いて、次の2種類の情報を入れます。

1つ目はGoogle Sheetsの情報です。

```toml
[google_sheets]
spreadsheet_id = "Google SheetsのURL内にある長いID"
worksheet_name = "シート1"
```

2つ目はサービスアカウントJSONの情報です。

JSONファイルに書かれている値を、同じ名前の項目へ移します。

特に注意する項目:

```toml
private_key = """-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----"""
client_email = "..."
```

`private_key` は3つのダブルクォート `"""` で囲むと貼り付けやすいです。

## よくあるエラー

### Google Sheetsに接続できません

多くの場合、次のどれかです。

- spreadsheet_idが違う
- worksheet_nameが違う
- Google Sheetsをサービスアカウントに共有していない
- Secretsの貼り付けで `private_key` が崩れている

### ModuleNotFoundError

`requirements.txt` がGitHubにアップロードされていない可能性があります。

### アプリは開くがデータが出ない

Google Sheetsの1行目が列名になっているか確認してください。

## 最初のゴール

最初は完璧な公開ではなく、次の状態を目標にします。

1. StreamlitのURLが開く
2. Google Sheetsのデータが1件ずつ表示される
3. `favorite` を押すとGoogle Sheetsが更新される
4. `user_note` を入力して更新するとGoogle Sheetsが更新される
