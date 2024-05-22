from fastapi import FastAPI, Request
from bs4 import BeautifulSoup
import requests
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/download", response_class=HTMLResponse)
async def scrape(request: Request):
    initial_url = request.query_params.get('id')
    if not initial_url:
        return HTMLResponse(content="<html><body><p>Error: No URL provided</p></body></html>", status_code=400)
    
    response = requests.get(initial_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        download_content = soup.find('div', class_='download-content')
        if download_content:
            link_tag = download_content.find('a', href=True)
            if link_tag:
                intermediate_href = link_tag['href']
                # Prepend base URL
                full_intermediate_url = f"https://d000d.com{intermediate_href}"

                # Fetch the intermediate URL
                second_response = requests.get(full_intermediate_url)
                if second_response.status_code == 200:
                    second_soup = BeautifulSoup(second_response.content, 'html.parser')
                    download_generated = second_soup.find('div', class_='download-generated')
                    if download_generated:
                        final_link_tag = download_generated.find('a', href=True)
                        if final_link_tag:
                            final_href = final_link_tag['href']
                            html_content = f'<html><body><a href="{final_href}" target="_blank">Download File</a></body></html>'
                            return HTMLResponse(content=html_content)
                        return HTMLResponse(content="<html><body><p>Error: Final download link not found</p></body></html>", status_code=404)
                else:
                    return HTMLResponse(content="<html><body><p>Error: Failed to fetch the intermediate URL</p></body></html>", status_code=500)
        return HTMLResponse(content="<html><body><p>Error: Download content not found</p></body></html>", status_code=404)
    else:
        return HTMLResponse(content="<html><body><p>Error: Failed to fetch the initial URL</p></body></html>", status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
