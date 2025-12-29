# 如何在 N8N 中建立 Workflow 來呼叫 Markitdown API

恭喜您成功將 Markitdown API 部署到 Zeabur！

本指南將詳細說明如何建立一個 N8N Workflow，透過 `HTTP Request` 節點來上傳文件並解析其內容。

## 步驟 1: 取得您在 Zeabur 上的 API URL

首先，您需要從 Zeabur 儀表板取得您服務的公開 URL。

1.  登入 [Zeabur 儀表板](https://dash.zeabur.com)。
2.  進入您的專案，然後點擊 `markitdown-api` 服務。
3.  在服務概覽頁面，找到並複製 "Domains" (網域) 下提供的 URL。它看起來會像 `https://<your-service-name>.zeabur.app`。

您的 API 端點 URL 將是 `YOUR_ZEABUR_URL/convert`。例如：`https://markitdown-api-123.zeabur.app/convert`。

## 步驟 2: 建立 N8N Workflow

現在，登入您的 N8N 實例並按照以下步驟操作。

### 1. 建立一個新的 Workflow

- 在您的 N8N 儀表板，點擊 "Add workflow" 建立一個新的空白工作流程。
- 預設會有一個 "Start" 節點。您可以直接用它來手動觸發。

### 2. 新增並設定 HTTP Request 節點

這是整個流程的核心。

1.  點擊 `+` 按鈕，然後搜尋並選擇 `HTTP Request` 節點。
2.  將 "Start" 節點的輸出端連接到 `HTTP Request` 節點的輸入端。
3.  點擊 `HTTP Request` 節點以開啟其設定面板，並填寫以下資訊：

    - **Authentication**: `None`
      *   我們的 API 不需要認證。

    - **Request Method**: `POST`
      *   因為我們要傳送資料來建立一個新的轉換任務。

    - **URL**: 貼上您在步驟 1 中取得的 API 端點 URL。
      *   例如：`https://markitdown-api-123.zeabur.app/convert`

    - **Send Body**: `On`
      *   我們需要傳送檔案內容。

    - **Body Content Type**: `Form-Data Multipart`
      *   這是上傳檔案時標準的格式。

        - **Parameters**:
        這一步是告訴 N8N 要將哪個檔案附加到請求中。

        1.  點擊下方的 **Add Parameter** 按鈕。
        2.  在跳出的選單中，您可能會看到不同的選項。根據您的 N8N 版本，它可能被稱為 `File` 或 `n8n Binary File`。**請選擇代表檔案/二進位資料的那個選項，在您的情況下，這應該是 `n8n Binary File`。**
        3.  設定欄位如下：
            - **Name**: 輸入 `file`
              - **極為重要**: 這是 API 規定的**參數名稱 (Key)**。您可以把它想像成一個欄位的標籤。無論您上傳什麼類型的檔案（`.docx`, `.pdf`, `.html` 等），這個名稱 **永遠都必須是 `file`**。您 **不需要** 為每種文件類型新增不同的參數。API 的設計就是只接收一個名為 `file` 的參數，然後它會自己分析檔案的內容和類型。
            - **Value**: 這裡需要填入檔案的二進位資料。
            - **Source of File**: 當您在上一步選擇了 `n8n Binary File` 後，這裡的選項可以讓您決定檔案從哪裡來。為了方便手動測試，請選擇 `From 'File Upload' Parameter`。這會讓您在執行 Workflow 時，N8N 會跳出一個對話框讓您上傳檔案。在真實的自動化流程中，檔案可能來自前一個節點（例如 Webhook），這時您會在這裡使用表達式（Expression）來引用該檔案的二進位資料。

    完成設定後，您的 `HTTP Request` 節點看起來應該像這樣：
    
    ![N8N HTTP Request Node Setup](https://i.imgur.com/Lz2zY6c.png) 
    *(這是一張示意圖，實際 UI 可能略有不同)*


### 3. 測試您的 Workflow

1.  點擊 N8N 畫面右上角的 **Execute workflow** 按鈕。
2.  N8N 會彈出一個視窗，因為您設定了 `From 'File Upload' Parameter`，它會要求您上傳一個檔案。
3.  選擇一個您想要測試的檔案（例如一個 `.docx` 或 `.pdf` 檔案）。
4.  點擊 "Execute"。

執行成功後，您可以在 `HTTP Request` 節點的 `Output` 分頁中看到 API 的回傳結果。它應該是一個 JSON 物件，如下所示：

```json
{
  "filename": "your_test_file.docx",
  "markdown": "這是從您的文件中解析出來的 Markdown 內容..."
}
```

## 步驟 3: 在 AI Agent 中使用解析後的內容

現在您已經成功獲取了文件的 Markdown 內容，您可以將它傳遞給下一個節點來建構您的 AI Agent。

**範例：將內容傳送給一個大型語言模型 (LLM)**

1.  在 `HTTP Request` 節點後新增一個節點（例如 `OpenAI`、`Google Gemini` 或另一個 `HTTP Request` 節點來呼叫您自己的 LLM API）。
2.  在 LLM 節點的 "Prompt" 欄位中，您可以使用 N8N 的表達式 (Expression) 來引用上一個節點的輸出。

    例如，要取得 Markdown 內容，您可以使用以下表達式：
    ```
    {{ $json["markdown"] }}
    ```
    或者透過拖曳的方式，將 `HTTP Request` 節點輸出中的 `markdown` 欄位拖到 Prompt 輸入框中。

3.  您可以設計一個 Prompt，例如：
    ```
    請根據以下文章內容，總結其核心要點：

    {{ $json["markdown"] }}
    ```

這樣，您就建立了一個完整的自動化流程：**上傳任意文件 -> 解析成純文字 -> 交給 AI 進行處理**。

您可以根據這個基礎，擴展出更複雜的應用，例如建立 RAG (Retrieval-Augmented Generation)、文件問答機器人等。
