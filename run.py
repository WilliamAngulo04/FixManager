import uvicorn

if __name__ == "__main__":
    # Al usar "app.main:app", uvicorn busca la carpeta app, 
    # luego el archivo main y dentro el objeto app.
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)