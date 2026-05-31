# 鎵嬫満璇煶杈撳叆 鈫?PC 杈撳叆妗?

PC 绔闊宠緭鍏ュ線寰€鍙楅害鍏嬮鏀堕煶璐ㄩ噺鎷栫疮锛岃瘑鍒晥鏋滀笉濡傛墜鏈恒€傝繖涓伐鍏疯浣犲湪 **鎵嬫満绯荤粺鑷甫鐨勮闊宠緭鍏ユ硶** 閲岃瀹屻€佹敼濂戒竴鏁存璇濓紝鐐?**鍙戦€佸埌鐢佃剳**锛屾枃瀛楅€氳繃灞€鍩熺綉鍐欏叆 PC 褰撳墠鐒︾偣杈撳叆妗嗭紙SendInput锛屼笉鐢ㄥ壀璐存澘锛夈€?

## 鐜瑕佹眰

- Windows 10/11
- Python 3.8+锛堟帹鑽?3.11+锛?
- 鎵嬫満涓?PC 杩炴帴 **鍚屼竴 Wi-Fi**锛堝叧闂瀹㈢綉缁滈殧绂伙級

## 瀹夎

```powershell
git clone https://github.com/step963121604/phone-to-pc-voice-input.git
cd phone-to-pc-voice-input
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r pc_agent\requirements.txt
```

## 鍚姩 PC Agent

```powershell
python -m pc_agent.main
```

鍙€夋寚瀹氱鍙ｏ紙榛樿 `8787`锛夛細

```powershell
python -m pc_agent.main 8787
```

### 寮€鏈鸿嚜鍚?

```powershell
python -m pc_agent.main --install-autostart
```

鍙栨秷锛歚python -m pc_agent.main --uninstall-autostart`  
涔熷彲鍦ㄦ墭鐩樿彍鍗曞嬀閫?**寮€鏈鸿嚜鍚?*锛堜娇鐢?`pythonw`锛岀櫥褰曞悗鏃犻粦绐楀彛锛夈€?

### 鎹㈣妯″紡锛圓gent 杈撳叆妗嗭級

榛樿 **Shift+Enter** 鎹㈣锛岄伩鍏?Enter 琚綋鎴愩€屽彂閫併€嶃€? 
鎵樼洏鑿滃崟鍙垏鎹細`Shift+Enter` / `Enter` / `绌烘牸`銆? 
閰嶇疆淇濆瓨鍦?`%USERPROFILE%\.phone-to-pc-voice-input\config.json`銆?

鍚姩鍚庯細

1. 绯荤粺鎵樼洏浼氬嚭鐜板浘鏍?
2. 鎺у埗鍙颁細鎵撳嵃 **鎵嬫満璁块棶閾炬帴** 鍜?**6 浣嶉厤瀵圭爜**
3. 鎵樼洏鑿滃崟鍙€屽湪娴忚鍣ㄦ墦寮€銆嶃€屽鍒堕摼鎺ャ€?

## 鎵嬫満浣跨敤

### 棣栨锛堢害 30 绉掞級

1. PC 鎵樼洏 鈫?**鎵嬫満鎵爜椤?*锛岀敤鎵嬫満鐩告満/寰俊鎵簩缁寸爜鎵撳紑  
   鎴栧鍒舵墭鐩橀噷鐨勯摼鎺ュ埌鎵嬫満娴忚鍣?
2. 鍦ㄩ〉闈㈠簳閮ㄥ睍寮€ **銆屾坊鍔犲埌涓诲睆骞曘€?*锛屾寜鎻愮ず淇濆瓨妗岄潰鍥炬爣  
3. 閰嶅鐮佷繚瀛樺湪 PC 鐨?`%USERPROFILE%\.phone-to-pc-voice-input\token.txt`锛?*閲嶅惎 Agent 涓嶅彉**锛屼功绛惧彲闀挎湡浣跨敤

### 鏃ュ父浣跨敤

1. 鍦?PC 涓婂厛鐐瑰紑瑕佽緭鍏ョ殑浣嶇疆
2. 鐐规墜鏈轰富灞忓箷 **銆屽彂PC銆?* 鍥炬爣锛?*涓嶈姣忔寮€ Chrome**锛岃交搴旂敤鏇寸渷鍐呭瓨锛?
3. 绯荤粺璇煶鍚啓 鈫?**鍙戦€佸埌鐢佃剳 鈻?*
4. 鍙戦€佹垚鍔熷悗鑷姩娓呯┖锛涘垏鍒板埆鐨?App 鏃朵細鑷姩鏂紑杩炴帴鐪佺數

> 鑻ュ閲岃矾鐢卞櫒缁?PC 鎹簡 IP锛岄渶閲嶆柊鎵爜鎴栨墦寮€鏂伴摼鎺ヤ竴娆°€?

### 鍏充簬鎵嬫満鍐呭瓨

- **涓诲睆骞曞浘鏍?* = 鍗曠嫭灏忕獥鍙ｏ紙PWA锛夛紝姣旀墦寮€鏁翠釜 Chrome 杞诲緱澶?
- 椤甸潰宸茬紦瀛橀潤鎬佽祫婧愶紝浜屾鎵撳紑鏇村揩
- 鑻ヤ粛瀚岄噸锛屽彧鑳藉仛鍘熺敓 App锛堜綋绉洿澶т絾鍙洿绮剧畝锛夛紱褰撳墠鏂规鍦ㄣ€岃兘璋冪敤绯荤粺璇煶閿洏銆嶅墠鎻愪笅宸茶緝杞?

## 鍗忚鎽樿

- 鎵嬫満 鈫?PC锛歚{ "t": "send", "text": "..." }`
- PC 鈫?鎵嬫満鎴愬姛锛歚{ "t": "ok", "ms": 45 }`锛堥殢鍚庢墜鏈烘竻绌?textarea锛?
- PC 鈫?鎵嬫満澶辫触锛歚{ "t": "err", "code": "inject_failed", "msg": "..." }`锛堜繚鐣欏師鏂囷級

## Android 鍘熺敓 App锛堟洿鐪佸唴瀛橈級

涓嶇敤姣忔寮€娴忚鍣紝瑙?[android/README.md](./android/README.md)銆?

- Android Studio 鎵撳紑 `android/` 鐩綍缂栬瘧锛屾垨瀹夎 `app-debug.apk`
- 棣栨鍦?App 閲屽～鍐?PC 鐨?IP銆佺鍙ｃ€侀厤瀵圭爜

## 鐩綍缁撴瀯

```
phone-to-pc-voice-input/
鈹溾攢鈹€ android/               # Android 鍘熺敓瀹㈡埛绔?
鈹溾攢鈹€ pc_agent/
鈹?  鈹溾攢鈹€ main.py          # 鎵樼洏 + 鍚姩鏈嶅姟
鈹?  鈹溾攢鈹€ server.py        # HTTP / WebSocket
鈹?  鈹溾攢鈹€ injector.py      # SendInput Unicode
鈹?  鈹斺攢鈹€ requirements.txt
鈹溾攢鈹€ web/
鈹?  鈹溾攢鈹€ index.html
鈹?  鈹斺攢鈹€ app.js
鈹斺攢鈹€ README.md
```

## 甯歌闂

| 鐜拌薄 | 澶勭悊 |
|------|------|
| 鎵嬫満鎵撲笉寮€缃戦〉 | 妫€鏌ュ悓涓€ Wi-Fi锛沇indows 闃茬伀澧欐斁琛?Python 涓撶敤缃戠粶 |
| 鏄剧ず鏈繛鎺?| 閾炬帴蹇呴』甯?`?token=`锛岀敤鎵樼洏澶嶅埗鐨勫畬鏁?URL |
| 瀛楁病杩涚洰鏍囨 | 鍙戦€佸墠鍦?PC 涓婂厛鐐逛竴涓嬬洰鏍囪緭鍏ユ |
| 娉ㄥ叆澶辫触 | 鍏堝湪璁颁簨鏈祴璇曪紱閮ㄥ垎 Electron 搴旂敤鍙兘涓嶅吋瀹?|

## 璁稿彲

[MIT](./LICENSE)
