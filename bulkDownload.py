import urllib.request, urllib.error, requests, json, sys, os, re, time

cubeId = sys.argv[1] #"SmallMagic"
cubeUrl = "https://cubecobra.com/cube/api/cubeJSON/" + cubeId
print(cubeUrl)
scryfallBaseUrl = "https://api.scryfall.com/cards/"
delaySeconds = 0.1
extendedDelaySeconds = 1
timeoutSeconds = 60
scryfallHeaders = {
    'Accept': '*/*',
    'User-Agent': 'CubeCobraDownloadImagesScript/1.0'
}
tokensProcessed = set()

def clean_filename(filename_string):
    name, ext = os.path.splitext(filename_string)
    
    cleaned_name = re.sub(r'[\ \/:\*\?"<>\|]', '_', name)
    cleaned_name = cleaned_name.strip('. ')
    
    if not cleaned_name:
        cleaned_name = str(timestamp_ms = time.time_ns() // 1_000_000)
        
    return cleaned_name + ext

def downloadCardImage(url, filename, folder):
    filename = clean_filename(filename)
    os.makedirs(folder, exist_ok=True)
    imageResponse = requests.get(url, headers=scryfallHeaders)
    if imageResponse.status_code == 200:
        with open(folder + "/" + filename, "wb") as file:
            file.write(imageResponse.content)
    else:
        print(f"Failed to retrieve image for {filename}. Status code: {imageResponse.status_code}")

with urllib.request.urlopen(cubeUrl, timeout=timeoutSeconds) as url:
    cubeCobraResponse = json.load(url)
    mainboardCards = cubeCobraResponse["cards"]["mainboard"]
    print(str(len(mainboardCards)) + " cards")
    
    progress = 1
    i = 0
    
    for card in mainboardCards:
        i = i + 1
        if(i == progress * 45):
            progress = progress + 1
            print(str(i) + " cards processed...")
        
        name = card["details"]["name"]
        scryfallId = card["details"]["scryfall_id"]
        filename = str(i) + "_" + name + ".jpg"
        scryfallUrl = scryfallBaseUrl + scryfallId
        time.sleep(delaySeconds)
        scryfallCardReq = urllib.request.Request(scryfallUrl, headers=scryfallHeaders)
        
        try:
            with urllib.request.urlopen(scryfallCardReq, timeout=timeoutSeconds) as url2:
                scryFallResponse = json.load(url2)
                frontImage = ""
                backImage = ""
                faces = None
                if "card_faces" in scryFallResponse:
                    faces = scryFallResponse["card_faces"]
                            
                if faces is not None and len(faces) > 1:
                    frontImage = faces[0]["image_uris"]["normal"]
                    backImage = faces[1]["image_uris"]["normal"]
                    downloadCardImage(frontImage, str(i) + "_" + name + "_front" + ".jpg", "dfc")
                    downloadCardImage(backImage, str(i) + "_" + name + "_back" + ".jpg", "dfc")
                else:
                    frontImage = scryFallResponse["image_uris"]["normal"]
                    downloadCardImage(frontImage, filename, "normal")
        except urllib.error.HTTPError as e:
            print(e.reason)
            if e.code == "429":
                print("retrying")
                time.sleep(extendedDelaySeconds)
                with urllib.request.urlopen(scryfallCardReq, timeout=timeoutSeconds) as url2:
                    scryFallResponse = json.load(url2)
                    frontImage = ""
                    backImage = ""
                    faces = None
                    if "card_faces" in scryFallResponse:
                        faces = scryFallResponse["card_faces"]
                                
                    if faces is not None and len(faces) > 1:
                        frontImage = faces[0]["image_uris"]["normal"]
                        backImage = faces[1]["image_uris"]["normal"]
                        downloadCardImage(frontImage, str(i) + "_" + name + "_front" + ".jpg", "dfc")
                        downloadCardImage(backImage, str(i) + "_" + name + "_back" + ".jpg", "dfc")
                    else:
                        frontImage = scryFallResponse["image_uris"]["normal"]
                        downloadCardImage(frontImage, filename, "normal")
        #handle tokens
        j = 0
        if "tokens" in card["details"]:
            tokens = card["details"]["tokens"]
            for token in tokens:
                j = j + 1
                time.sleep(delaySeconds)
                tokenScryfallUrl = scryfallBaseUrl + token
                tokenScryfallCardReq = urllib.request.Request(tokenScryfallUrl, headers=scryfallHeaders)
                try:
                    with urllib.request.urlopen(tokenScryfallCardReq, timeout=timeoutSeconds) as url3:
                        tokenScryFallResponse = json.load(url3)
                        oracleId = tokenScryFallResponse["oracle_id"]
                        if oracleId in tokensProcessed:
                            continue
                        tokensProcessed.add(oracleId)
                        frontImage = ""
                        backImage = ""
                        tokenName = tokenScryFallResponse["name"]
                        faces = None
                        if "card_faces" in tokenScryFallResponse:
                            faces = tokenScryFallResponse["card_faces"]
                        
                        if faces is not None and len(faces) > 1:
                            frontImage = faces[0]["image_uris"]["normal"]
                            backImage = faces[1]["image_uris"]["normal"]
                            downloadCardImage(frontImage, tokenName + "_" + oracleId + "_front" + ".jpg", "tokens/dfc")
                            downloadCardImage(backImage, tokenName + "_" + oracleId + "_back" + ".jpg", "tokens/dfc")
                        else:
                            frontImage = tokenScryFallResponse["image_uris"]["normal"]
                            downloadCardImage(frontImage, tokenName + "_" + oracleId + ".jpg", "tokens/normal")
                except urllib.error.HTTPError as e:
                    print(e.reason)
                    if e.code == "429":
                        print("retrying")
                        time.sleep(extendedDelaySeconds)
                        with urllib.request.urlopen(tokenScryfallCardReq, timeout=timeoutSeconds) as url3:
                            tokenScryFallResponse = json.load(url3)
                            oracleId = tokenScryFallResponse["oracle_id"]
                            if oracleId in tokensProcessed:
                                continue
                            tokensProcessed.add(oracleId)
                            frontImage = ""
                            backImage = ""
                            tokenName = tokenScryFallResponse["name"]
                            faces = None
                            if "card_faces" in tokenScryFallResponse:
                                faces = tokenScryFallResponse["card_faces"]
                            
                            if faces is not None and len(faces) > 1:
                                frontImage = faces[0]["image_uris"]["normal"]
                                backImage = faces[1]["image_uris"]["normal"]
                                downloadCardImage(frontImage, tokenName + "_" + oracleId + "_front" + ".jpg", "tokens/dfc")
                                downloadCardImage(backImage, tokenName + "_" + oracleId + "_back" + ".jpg", "tokens/dfc")
                            else:
                                frontImage = tokenScryFallResponse["image_uris"]["normal"]
                                downloadCardImage(frontImage, tokenName + "_" + oracleId + ".jpg", "tokens/normal")

print("Done!")