# 將 Markitdown API 部署到 Zeabur

現在您的專案已經準備好部署了。請遵循以下步驟將您的 FastAPI 應用程式部署到 Zeabur。

## 步驟 1: 將您的程式碼推送到 GitHub

Zeabur 會從您的 GitHub 儲存庫部署您的應用程式。

1.  **初始化 Git (如果尚未完成)**
    如果您還沒有這樣做，請在您的專案根目錄中初始化 Git。
    ```bash
    git init
    ```

2.  **新增、提交和推送您的變更**
    將所有檔案新增到暫存區，包括我們剛剛建立的 `api_server.py`、`zeabur.json` 和修改後的 `Dockerfile` 與 `pyproject.toml`。

    ```bash
    git add .
    git commit -m "feat: Add FastAPI server for Zeabur deployment"
    ```

3.  **在 GitHub 上建立一個新的儲存庫**
    - 前往 [GitHub](https://github.com/new) 並建立一個新的儲存庫 (例如，`markitdown-api`)。
    - **不要** 使用 README、.gitignore 或 License 初始化它，因為您的專案已經有了這些。

4.  **將您本地的儲存庫連接到 GitHub**
    將 `YOUR_GITHUB_USERNAME` 和 `YOUR_REPOSITORY_NAME` 替換為您的實際資訊。

    ```bash
    git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPOSITORY_NAME.git
    git branch -M main
    git push -u origin main
    ```

## 步驟 2: 在 Zeabur 上部署

1.  **登入 Zeabur**
    - 前往 [Zeabur 儀表板](https://dash.zeabur.com) 並使用您的 GitHub 帳戶登入。

2.  **建立一個新專案**
    - 在您的儀表板上，點擊 "專案" (Projects)，然後點擊 "建立新專案" (Create New Project)。給它取一個您喜歡的名字。

3.  **部署您的服務**
    - 進入您的新專案後，點擊 "部署新服務" (Deploy New Service) 或 "從 GitHub 新增" (Add from GitHub)。
    - 選擇您剛剛建立的 `markitdown-api` 儲存庫。
    - Zeabur 將會讀取您的 `zeabur.json` 檔案並開始使用 `Dockerfile` 進行建置。

4.  **完成！**
    - Zeabur 會自動處理建置和部署過程。完成後，它會為您的 API 提供一個公開的 URL。
    - 您可以在 Zeabur 儀表板的服務視圖中找到這個 URL。

## 步驟 3: 在 N8N 中使用您的 API

部署完成後，您的 API 將在 Zeabur 提供的 URL 上可用。您可以在 N8N 的 HTTP Request 節點中使用此 URL 來與您的 `markitdown` 服務進行互動。

- **URL**: `https://YOUR_ZEABUR_APP_URL/upload/`
- **方法**: `POST`
- **Body**: `Form-Data` / `multipart/form-data`
    - **金鑰**: `file`
    - **值**: 選擇您要上傳的檔案。
