import os, platform, time, datetime, pprint, json, math, requests, path, socket, random
from time import sleep
import numpy as np, pandas as pd
import selenium.webdriver as webdriver
from flask import Flask, request, jsonify, render_template
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome import service
from selenium.webdriver.chrome import service as fs
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException,NoSuchElementException,ElementNotInteractableException
from selenium.common import exceptions  
import os.path, config

app = Flask(__name__)

@app.route('/', methods=['POST'])
def webhook():

    global range_1
    global range_2
    global range_3
    global range_4
    global range_5
    global NetProfit
    global MaxDrawdown
    global SortinoRatio
    global ProfitFactor
    global TotalClosedTrades
    global PercentProfitable
    global AvgTrade
    global LargestLosingTrade
    global OpenPL
    global AvgBarsInTrades
    global AvgBarsInWinningTrades
    global AvgBarsInLosingTrades

    global SymbolName

    host    = socket.gethostname()
    data    = json.loads(request.data)

    # =======================================================================================
                                    # INPUT #
    # =======================================================================================

    user        = config.USER
    pw          = config.PW
    tf          = "1 minute" 
    source      = "Binance"
    startYear   = "2021"
    startMonth  = "01"
    startDay    = "01"

    if data["chart"] == "ReverseLong":
        chart = "UezAI0Wc"
    if data["chart"] == "ReverseShort":
        chart = "i2e8aLfZ"
    if data["chart"] == "FollowLong":
        chart = "oBtlr9Ob"
    if data["chart"] == "FollowShort":
        chart = "tBxqeyVS"

    flagID    = data["flagID"]      

    Strategy_p1_max  = int(data["Strategy_p1_max"] )                                                             
    Strategy_p1_min  = int(data["Strategy_p1_min"] )   
    Strategy_p1_cut  = int(data["Strategy_p1_cut"] ) 
    Strategy_p1_step = int(round(Strategy_p1_max  - Strategy_p1_min )/Strategy_p1_cut)                                                        
                                                                                    
    Strategy_p2_max  = int(data["Strategy_p2_max"] )                                                           
    Strategy_p2_min  = int(data["Strategy_p2_min"] )
    Strategy_p2_cut  = int(data["Strategy_p2_cut"] )
    Strategy_p2_step = int(round(Strategy_p2_max - Strategy_p2_min)/Strategy_p2_cut)
                                                                                                
    SLOW_max = int(data["SLOW_max"] )
    SLOW_min = int(data["SLOW_min"] )
    SLOW_cut = int(data["SLOW_cut"] )
    SLOW_step = int(round(SLOW_max - SLOW_min)/SLOW_cut)
    SLOW_cut_Finalize = int(data["SLOW_cut_Finalize"] )

    CORE_max = int(data["CORE_max"] )
    CORE_min = int(data["CORE_min"] )
    CORE_cut = int(data["CORE_cut"] )
    CORE_step = int(round(CORE_max - CORE_min)/CORE_cut)
    CORE_cut_Finalize = int(data["CORE_cut_Finalize"] )  

    BAND_max = int(data["BAND_max"] )
    BAND_min = int(data["BAND_min"] )
    BAND_cut = int(data["BAND_cut"] )
    BAND_step = int(round(BAND_max - BAND_min)/BAND_cut)
    BAND_cut_Finalize = int(data["BAND_cut_Finalize"]  )

    #Final cut
    Strategy_p1_cut_Finalize = int(data["Strategy_p1_cut_Finalize"] )
    Strategy_p2_cut_Finalize = int(data["Strategy_p2_cut_Finalize"] )

    # =======================================================================================
                                    # Filter INPUT #
    # =======================================================================================

    Filter_ProfitFactor          = float(data["Filter_ProfitFactor"] )
    Filter_SortinoRatio          = float(data["Filter_SortinoRatio"] )
    Filter_MaxDrawdown           = float(data["Filter_MaxDrawdown"] )
    Filter_TotalClosedTrades     = float(data["Filter_TotalClosedTrades"] ) # drop -> if less than 60% of the closedTrades Avarage
    Filter_PercentProfitable     = float(data["Filter_PercentProfitable"] )
    Filter_OpenPL                = float(data["Filter_OpenPL"] )
    Filter_TotalClosedTrades_Min = float(data["Filter_TotalClosedTrades_Min"] )

    Filter_Finalize_ProfitFactor = float(data["Filter_Finalize_ProfitFactor"] )
    Filter_Finalize_SortinoRatio = float(data["Filter_Finalize_SortinoRatio"] )

    # =======================================================================================
    # =======================================================================================

    def now():
        t_delta = datetime.timedelta(hours=9)
        JST     = datetime.timezone(t_delta, 'JST')
        now     = datetime.datetime.now(JST)
        return now.time().strftime('%X')

    def check_exists_by_xpath(xpath):
        try:
            browser.find_element(By.XPATH, value=xpath)
        except NoSuchElementException:
            return False
        return True

    def check_exists_by_classname(classname):
        try:
            browser.find_element(By.CLASS_NAME, value=classname)
        except NoSuchElementException:
            return False
        return True

    def get_StrategyName():
        browser.find_element(By.XPATH, value=path.StrategyNameNow).text

    def click_NextSymbol(x):
        browser.find_element(By.XPATH, value=f"//div[2]/div[6]/div/div[1]/div[1]/div[1]/div[1]/div[2]/div/div[2]/div/div/div[2]/div/div[{x}]/div/div").click()

    def click_ParamMenu():
        browser.find_element(By.XPATH, value=path.ParamMenu).click()

    def click_Generate():
        browser.find_element(By.XPATH, value=path.Generate).click()

    def click_Alert():
        browser.find_element(By.XPATH, value=path.Alert).click()

    def click_SubmitParam():
        browser.find_element(By.NAME,value="submit").click()

    def click_Disconect():
        browser.find_element(By.XPATH, value=path.Disconect).click()
        sleep(3)

    def flagcounter(flag):
        browser.find_element(By.XPATH,value=path.flagmenu).click() 
        sleep(1)
        flags = browser.find_element(By.XPATH, value= f"/html/body/div[5]/div/span/div[1]/div/div/div[{flag + 3}]/div[2]/span").text
        flags = int(flags)
        return flags

    def apply_range():
        global range_1
        global range_2
        global range_3
        global range_4
        global range_5
        range_1 = range(Strategy_p1_min, Strategy_p1_max+1, Strategy_p1_step) 
        range_2 = range(Strategy_p2_min, Strategy_p2_max+1, Strategy_p2_step) 
        range_3 = range(SLOW_min,        SLOW_max+1,        SLOW_step)
        range_4 = range(CORE_min,        CORE_max+1,        CORE_step)
        range_5 = range(BAND_min,        BAND_max+1,        BAND_step)

    def input_Param(where,param_ID):
        for i in range(3):
            try:
                elem_Options = browser.find_elements(By.CLASS_NAME, value='light-button-1f5iHRsw')
                elem_Options[0].click()
                if param_ID == param_1:
                    P1 = browser.find_element(By.XPATH, value=f'//div[{where*2}]/div/span/span[1]/input')
                    P1.send_keys(Keys.CONTROL,"a")
                    P1.send_keys(Keys.BACK_SPACE)
                    P1.send_keys(param_1, Keys.ENTER)
                elif param_ID == param_2:
                    P2 = browser.find_element(By.XPATH, value=f'//div[{where*2}]/div/span/span[1]/input')
                    P2.send_keys(Keys.CONTROL,"a")
                    P2.send_keys(Keys.BACK_SPACE)
                    P2.send_keys(param_2, Keys.ENTER)
                elif param_ID == param_3:
                    P3 = browser.find_element(By.XPATH, value=f'//div[{where*2}]/div/span/span[1]/input')
                    P3.send_keys(Keys.CONTROL,"a")
                    P3.send_keys(Keys.BACK_SPACE)
                    P3.send_keys(param_3, Keys.ENTER)
                elif param_ID == param_4:
                    P4 = browser.find_element(By.XPATH, value=f'//div[{where*2}]/div/span/span[1]/input')
                    P4.send_keys(Keys.CONTROL,"a")
                    P4.send_keys(Keys.BACK_SPACE)
                    P4.send_keys(param_4, Keys.ENTER)
                elif param_ID == param_5:
                    P5 = browser.find_element(By.XPATH, value=f'//div[{where*2}]/div/span/span[1]/input')
                    P5.send_keys(Keys.CONTROL,"a")
                    P5.send_keys(Keys.BACK_SPACE)
                    P5.send_keys(param_5, Keys.ENTER)
                break
            except exceptions.NoSuchElementException as e:
                if check_exists_by_xpath(path.Disconect):
                    browser.find_element(By.XPATH, value=path.Disconect).click()

    def result():
        global NetProfit
        global MaxDrawdown
        global SortinoRatio
        global ProfitFactor
        global TotalClosedTrades
        global PercentProfitable
        global AvgTrade
        global LargestLosingTrade
        global OpenPL
        global AvgBarsInTrades
        global AvgBarsInWinningTrades
        global AvgBarsInLosingTrades
        browser.implicitly_wait(1)
        NetProfit               = browser.find_element(By.XPATH, value=path.NetProfit).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        MaxDrawdown             = browser.find_element(By.XPATH, value=path.MaxDrawdown).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        SortinoRatio            = browser.find_element(By.XPATH, value=path.SortinoRatio).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        ProfitFactor            = browser.find_element(By.XPATH, value=path.ProfitFactor).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        TotalClosedTrades       = browser.find_element(By.XPATH, value=path.TotalClosedTrades).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        PercentProfitable       = browser.find_element(By.XPATH, value=path.PercentProfitable).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        AvgBarsInTrades         = browser.find_element(By.XPATH, value=path.AvgBarsInTrades).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        AvgBarsInWinningTrades  = browser.find_element(By.XPATH, value=path.AvgBarsInWinningTrades).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        AvgBarsInLosingTrades   = browser.find_element(By.XPATH, value=path.AvgBarsInLosingTrades).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        
        if check_exists_by_xpath(path.AvgTrade):
            AvgTrade            = browser.find_element(By.XPATH, value=path.AvgTrade).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        elif check_exists_by_xpath(path.AvgTrade):
            AvgTrade            = 0

        if check_exists_by_xpath(path.LargestLosingTrade):
            LargestLosingTrade  = browser.find_element(By.XPATH, value=path.LargestLosingTrade).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        elif check_exists_by_xpath(path.NaN_LargestLosingTrade):
            LargestLosingTrade  = 0
        
        if check_exists_by_xpath(path.OpenPL):
            OpenPL  = browser.find_element(By.XPATH, value=path.OpenPL).text.replace("−","-").replace("%","").replace("N/A","0").replace("$","")
        elif check_exists_by_xpath(path.NaN_OpenPL):
            OpenPL  = 0

    def Discord_Stream(username,avater,content):
        main_content = {
        "username":     f"{username}@{host}",
        "avatar_url":   avater,
        "content":      f"{present}   {content}   [{round((time.time() - start)/60)}/{estimateMinute}']  "}
        requests.post(path.Discord,main_content)

    def Discord_Alert(username,avater,content):
        main_content = {
        "username":     f"{username}@{host}",
        "avatar_url":   avater,
        "content":      f"{content}"}
        requests.post(path.Discord_Alert,main_content)

    def csv(df,windows,linux):
        if os.name == "nt":
            df.to_csv(windows, header=True, index=False)
        if os.name == "posix":
            df.to_csv(linux, header=True, index=False)

    def count_backtests():
        Count_Qualify   = (Strategy_p1_cut+1)*(Strategy_p2_cut+1)*(SLOW_cut+1)*(CORE_cut+1)*(BAND_cut+1)
        Count_Finalize  = (Strategy_p1_cut_Finalize+1)*(Strategy_p2_cut_Finalize+1)*(SLOW_cut_Finalize+1)*(CORE_cut_Finalize+1)*(BAND_cut_Finalize+1)
        backtests = Count_Qualify + Count_Finalize
        return backtests

    def export_result(dir_data,sorce_df):
        if dir_data == "All":
            file_Name = f"-All.csv"
            dir_Name  = dir_All
            df_Name   = df_All
        if dir_data == "Symbol":
            file_Name = f"{SymbolName}.csv"
            dir_Name  = dir_All
            df_Name   = df_Symbol
        if dir_data == "Qualify":
            file_Name = f"{SymbolName}_Qualify.csv"
            dir_Name  = dir_Qualify
            df_Name   = df_Filter
        if dir_data == "Finalize":
            file_Name = f"{SymbolName}_Finalize.csv"
            dir_Name  = dir_Finalize
            df_Name   = df_Filter
        if dir_data == "Activate":
            file_Name = "Activate.csv"
            dir_Name  = dir_Activate
            df_Name   = df_Activate

        if os.name == "nt":
            windows_dir_Name = f"{dir_db}\\{dir_Strategy}\\{StrategyName}\\{dir_Name}\\{file_Name}"
            CheckExists_ActivateCSV  = os.path.exists(windows_dir_Name)
            if CheckExists_ActivateCSV == True:
                df_Name = pd.read_csv(windows_dir_Name)
            else:
                df_Name = pd.DataFrame(frame, index=[])
        else:
            linux_dir_Name = f"{dir_db}/{dir_Strategy}/{StrategyName}/{dir_Name}/{file_Name}"
            CheckExists_ActivateCSV  = os.path.exists(linux_dir_Name) 
            if CheckExists_ActivateCSV == True:
                df_Name = pd.read_csv(linux_dir_Name)
            else:
                df_Name = pd.DataFrame(frame, index=[])

        df_Name = pd.concat([df_Name,sorce_df],axis=0).reset_index(drop=True)
        csv(df_Name, f"{dir_db}\\{dir_Strategy}\\{StrategyName}\\{dir_Name}\\{file_Name}", f"{dir_db}/{dir_Strategy}/{StrategyName}/{dir_Name}/{file_Name}")

    def get_SymbolName():
        global SymbolName
        SymbolName = browser.find_element(By.XPATH, value='//div[contains(@class,"text-IQnsk0hp")]').text
        print(f'\n Scanning -> {SymbolName}')
        Discord_Alert(SymbolName, path.AvatarSymbol, "Scanning...")

#################################################################################################################
##########    [1] LOGIN     #####################################################################################
#################################################################################################################

    print("Starting")
    Discord_Alert("Starting", path.AvatarLogin, "Starting!")
    start   = time.time() 
    today   = datetime.date.today() 

    for _ in range(3):
        try:
            if os.name == "posix":
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')  
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                CHROMEDRIVER = '/opt/chrome/chromedriver'
                chrome_service = fs.Service(executable_path=CHROMEDRIVER) 
                browser = webdriver.Chrome(service=chrome_service, options=options)
            if os.name == "nt":
                browser = webdriver.Chrome(r"C:\Users\daiki\Music\chromedriver.exe") 
            
            browser.implicitly_wait(10)

            browser.set_window_size('1500', '1500')
            browser.get(f"https://www.tradingview.com/chart/{chart}#signin")
            browser.find_element(By.CLASS_NAME, value="tv-signin-dialog__social.tv-signin-dialog__toggle-email.js-show-email").click()
            browser.find_element(By.NAME, value="username").send_keys(user)
            browser.find_element(By.NAME,value="password").send_keys(pw)
            browser.find_element(By.XPATH, value="//button[@type='submit']").click()

            try:
                browser.implicitly_wait(60)
                browser.find_element(By.XPATH,value=path.closeBottomTab).click() 
            except:
                pass

            browser.implicitly_wait(60)
            elem_ftMenu = browser.find_elements(By.XPATH,value=path.timeframeList) 
            browser.implicitly_wait(60)
            elem_ftMenu[1].click()
            browser.implicitly_wait(60)
            browser.find_element(By.XPATH,value=f'//div[.="{tf}"]').click()
            browser.implicitly_wait(60)
            browser.find_element(By.XPATH,value=path.openBottomTab).click() 

            flag    = int(flagID.replace('"',''))

            browser.implicitly_wait(60)
            browser.find_element(By.XPATH,value=path.watchlistMenu).click()
            browser.implicitly_wait(60)
            watchlists = browser.find_elements(By.CLASS_NAME, value='title-08JkF94b') # select flag
            browser.implicitly_wait(60)
            watchlists[flag].click()

            try:
                browser.implicitly_wait(3)
                browser.find_element(By.XPATH,value='//button[2][.="Performance Summary"]').click()
                sleep(1)
            except:
                browser.implicitly_wait(3)
                browser.find_element(By.XPATH,value=path.strategyTester).click()
                sleep(2)
                browser.find_element(By.XPATH,value='//button[2][.="Performance Summary"]').click()
                sleep(2)

            for i in range(3):
                print(f"deephistory click attempts -> {i}") 
                sleep(0.5)
                if check_exists_by_classname("backtesting-content-wrapper.widgetContainer-C69P68Cf"):
                    browser.find_element(By.XPATH, value=path.deepHistory).click()
                    sleep(0.5)
                if check_exists_by_classname("backtesting-content-wrapper.widgetContainer-C69P68Cf.hidden-C69P68Cf"):
                    break 

            browser.find_element(By.XPATH, value=path.testStartDate).click()
            elem_testStart = browser.find_element(By.CLASS_NAME, value="input-uGWFLwEy.with-end-slot-uGWFLwEy")
            elem_testStart.send_keys(Keys.CONTROL,"a")
            elem_testStart.send_keys(Keys.BACK_SPACE)
            elem_testStart.send_keys(startYear)
            elem_testStart.send_keys(startMonth)
            elem_testStart.send_keys(startDay)

            flags = flagcounter(flag)
            browser.find_element(By.XPATH,value=path.flagmenu).click()

            StrategyName  = browser.find_element(By.XPATH, value=path.StrategyNameNow).text

            backtests           = count_backtests()
            attempts            = backtests* flags
            scanTime            = 10
            estimateMinute      = round((attempts*scanTime)/60)
            estimateHour        = round(estimateMinute/60)
            scanInfo = f"\nStrategy:{StrategyName}\nflagID:{flagID}\nflags:{flags}\nbacktests:{backtests}\nattempts:{attempts}\nestimate:{estimateMinute}/min\n({estimateHour}/hour)\n"

            dir_db        = "data"
            dir_All       = 'All'
            dir_Qualify   = 'Qualify'
            dir_Finalize  = 'Finalize'
            dir_Activate  = 'Activate'

            if "ReverseLong" in StrategyName: 
                dir_Strategy  = "ReverseLong"
            if "ReverseShort" in StrategyName: 
                dir_Strategy  = "ReverseShort"
            if "FollowLong" in StrategyName: 
                dir_Strategy  = "FollowLong"
            if "FollowShort" in StrategyName: 
                dir_Strategy  = "FollowShort"

            if os.name == "nt":
                os.makedirs(f"{dir_db}\\{dir_Strategy}\\{StrategyName}\\{dir_All}",      exist_ok=True)
                os.makedirs(f"{dir_db}\\{dir_Strategy}\\{StrategyName}\\{dir_Qualify}",  exist_ok=True)
                os.makedirs(f"{dir_db}\\{dir_Strategy}\\{StrategyName}\\{dir_Finalize}", exist_ok=True)
                os.makedirs(f"{dir_db}\\{dir_Strategy}\\{StrategyName}\\{dir_Activate}", exist_ok=True)
            if os.name == "posix":
                os.makedirs(f"{dir_db}/{dir_Strategy}/{StrategyName}/{dir_All}",       exist_ok=True)
                os.makedirs(f"{dir_db}/{dir_Strategy}/{StrategyName}/{dir_Qualify}",   exist_ok=True)
                os.makedirs(f"{dir_db}/{dir_Strategy}/{StrategyName}/{dir_Finalize}",  exist_ok=True)
                os.makedirs(f"{dir_db}/{dir_Strategy}/{StrategyName}/{dir_Activate}",  exist_ok=True)

        except exceptions.NoSuchElementException as e:
            
            browser.quit()
            sleep(3)
        else:
            break
    else:
        Discord_Alert("Login Failed.",path.AvatarFailed,f"Login Faild. reason: {e}")

    print(f" \n{scanInfo}\n \n ")
    main_content = {
        "username":     f"Login Success @{host}",
        "avatar_url":   path.AvatarLogin,
        "content":      scanInfo}

    requests.post(path.Discord,      main_content)
    requests.post(path.Discord_Alert,main_content)

    #################################################################
        ##########       　    [2] SCAN              #########
    #################################################################

    frame = {'date': [],'strategy': [],'symbol': [],'Param_1': [],'Param_2': [],'param_3': [],'param_4': [],'param_5': [],\
            'NetProfit':[],'MaxDrawdown':[], 'SortinoRatio': [],'ProfitFactor': [], 'TotalClosedTrades': [],'PercentProfitable': [],\
            'AvgTrade': [],'LargestLosingTrade': [],'AvgBarsInTrades': [],'AvgBarsInWinningTrades': [],'AvgBarsInLosingTrades': [],'OpenPL': []}

    error = ''
    try:
        df_All      = pd.DataFrame(frame, index=[])
        df_Activate = pd.DataFrame(frame, index=[])
        symbols     = range(2, flags + 2, 1 )

        for SymbolNum in symbols:
            try:
                click_NextSymbol(SymbolNum)
            except:
                click_Disconect()
                click_NextSymbol(SymbolNum)

            sleep(2)

            get_SymbolName()

            df_Symbol = pd.DataFrame(frame, index=[]) # reset last symbol's dataframe before storing new symbol's data
            df_Filter = pd.DataFrame(frame, index=[]) # reset last finalized dataframe before storing new symbol's filter data

            apply_range()
            
            for param_1 in range_1:
                input_Param(1,param_1)
                for param_2 in range_2:
                    input_Param(2,param_2)
                    for param_3 in range_3:
                        input_Param(3,param_3)
                        for param_4 in range_4:
                            input_Param(4,param_4)
                            for param_5 in range_5:
                                input_Param(5,param_5)
                                click_SubmitParam()
                                click_Generate()
                                timerStart = time.time()
                                
                                for _ in range(60):
                                    try:
                                        result()
                                    except exceptions.NoSuchElementException as e:
                                        if check_exists_by_xpath(path.Disconect):
                                            browser.find_element(By.XPATH, value=path.Disconect).click()
                                            NetProfit = MaxDrawdown = SortinoRatio = ProfitFactor = TotalClosedTrades = PercentProfitable = AvgTrade = LargestLosingTrade = OpenPL= AvgBarsInTrades=AvgBarsInWinningTrades=AvgBarsInLosingTrades=0
                                        if check_exists_by_xpath(path.spin) == False:
                                            sleep(1)
                                            if check_exists_by_xpath(path.spin) == False:
                                                break
                                    else:
                                        break

                                series = [today,StrategyName,SymbolName,param_1,param_2,param_3,param_4,param_5,\
                                        float(NetProfit),float(MaxDrawdown),float(SortinoRatio),float(ProfitFactor),float(TotalClosedTrades),\
                                        float(PercentProfitable),float(AvgTrade),float(LargestLosingTrade),float(AvgBarsInTrades),\
                                        float(AvgBarsInWinningTrades),float(AvgBarsInLosingTrades),float(OpenPL)]   

                                s      = pd.Series(series, index=df_All.columns)
                                df_s   = pd.DataFrame(s).T

                                export_result("All",df_s)
                                export_result("Symbol",df_s)

                                passedTime  = time.time()
                                timerStop   = time.time()
                                sofar       = round((passedTime - start)/60,1)
                                scanTime    = round(timerStop - timerStart,1)
                                present     = now()
                                if NetProfit != 0:
                                    dataExists = "OK"
                                else:
                                    dataExists = "-----"
                                print(df_s)
                                Discord_Stream(SymbolName, path.AvatarParam, f"{scanTime}s, {dataExists}")

                    ##############          
            ######  [3] Qualify   #######
                    ##############          
            df_Filter = df_Symbol.sort_values(by="NetProfit", ascending=False)
            df_Filter.drop(df_Filter.loc[df_Filter['NetProfit']==0].index, inplace=True)
            df_Filter.drop(df_Filter.loc[df_Filter['ProfitFactor']<=Filter_ProfitFactor].index, inplace=True)
            df_Filter.drop(df_Filter.loc[df_Filter['SortinoRatio']<=Filter_SortinoRatio].index, inplace=True)
            mean_df_Filter = df_Filter['TotalClosedTrades'].mean() # mean after DROPPed.
            df_Filter.drop(df_Filter.loc[df_Filter['MaxDrawdown']>=Filter_MaxDrawdown].index, inplace=True)
            df_Filter.drop(df_Filter.loc[df_Filter['TotalClosedTrades']<=mean_df_Filter*Filter_TotalClosedTrades].index, inplace=True)
            df_Filter.drop(df_Filter.loc[df_Filter['TotalClosedTrades']<=Filter_TotalClosedTrades_Min].index, inplace=True)
            df_Filter.drop(df_Filter.loc[df_Filter['PercentProfitable']<=Filter_PercentProfitable].index, inplace=True)
            df_Filter.drop(df_Filter.loc[df_Filter['LargestLosingTrade']==0].index, inplace=True)
            df_Filter.drop(df_Filter.loc[df_Filter['OpenPL']<=Filter_OpenPL].index, inplace=True)
            df_Filter.reset_index(drop=True, inplace=True)

            export_result("Qualify",df_Filter)

            ###################################
            ##########  [4]Finalize   #########
            ###################################

            try:
                StrategyName = df_Filter.iloc[0, 1]
                SymbolName   = df_Filter.iloc[0, 2]
                param_1 = int(df_Filter.iloc[0, 3])
                param_2 = int(df_Filter.iloc[0, 4])
                param_3 = int(df_Filter.iloc[0, 5])
                param_4 = int(df_Filter.iloc[0, 6])
                param_5 = int(df_Filter.iloc[0, 7])

                step_p1 = Strategy_p1_step
                step_p2 = Strategy_p2_step
                step_p3 = SLOW_step
                step_p4 = CORE_step
                step_p5 = BAND_step

                p1_max  = int(param_1 + step_p1)
                p1_min  = int(param_1 - step_p1)
                p1_step = int(round(p1_max-p1_min)/Strategy_p1_cut_Finalize)
                range_1 = range(p1_min, p1_max+1, p1_step) 

                p2_max  = int(param_2 + step_p2)
                p2_min  = int(param_2 - step_p2)
                p2_step = int(round(p2_max-p2_min)/Strategy_p2_cut_Finalize)
                range_2 = range(p2_min, p2_max+1, p2_step)

                p3_max  = int(param_3 + step_p3)
                p3_min  = int(param_3 - step_p3)
                p3_step = int(round(p3_max-p3_min)/SLOW_cut_Finalize)
                range_3 = range(p3_min, p3_max+1, p3_step)

                p4_max  = int(param_4 + step_p4)
                p4_min  = int(param_4 - step_p4)
                p4_step = int(round(p4_max-p4_min)/CORE_cut_Finalize)
                range_4 = range(p4_min, p4_max+1, p4_step)

                p5_max  = int(param_5 + step_p5)
                p5_min  = int(param_5 - step_p5)
                p5_step = int(round(p5_max-p5_min)/BAND_cut_Finalize)
                range_5 = range(p5_min, p5_max+1, p5_step)

                df_Filter = pd.DataFrame(frame, index=[]) #reset Qualified dataframe before storing finalized data.

                for param_1 in range_1:
                    input_Param(1,param_1)
                    for param_2 in range_2:
                        input_Param(2,param_2)
                        for param_3 in range_3:
                            input_Param(3,param_3)
                            for param_4 in range_4:
                                input_Param(4,param_4)
                                for param_5 in range_5:
                                    input_Param(5,param_5)
                                    click_SubmitParam()
                                    click_Generate()
                                    timerStart = time.time()
                                    
                                    for _ in range(60):
                                        try:
                                            result()
                                        except exceptions.NoSuchElementException as e:
                                            if check_exists_by_xpath(path.Disconect):
                                                browser.find_element(By.XPATH, value=path.Disconect).click()
                                                NetProfit = MaxDrawdown = SortinoRatio = ProfitFactor = TotalClosedTrades = PercentProfitable \
                                                    = AvgTrade = LargestLosingTrade = OpenPL= AvgBarsInTrades=AvgBarsInWinningTrades=AvgBarsInLosingTrades=0
                                            if check_exists_by_xpath(path.spin) == False:
                                                sleep(1)
                                                if check_exists_by_xpath(path.spin) == False:
                                                    break
                                        else:
                                            break

                                    series = [today,StrategyName,SymbolName,param_1,param_2,param_3,param_4,param_5,\
                                            float(NetProfit),float(MaxDrawdown),float(SortinoRatio),float(ProfitFactor),float(TotalClosedTrades),\
                                            float(PercentProfitable),float(AvgTrade),float(LargestLosingTrade),float(AvgBarsInTrades),\
                                            float(AvgBarsInWinningTrades),float(AvgBarsInLosingTrades),float(OpenPL)] 

                                    s       = pd.Series(series, index=df_All.columns)
                                    df_s    = pd.DataFrame(s).T

                                    df_All     = pd.concat([df_All,df_s],axis=0).reset_index(drop=True)
                                    df_Symbol  = pd.concat([df_Symbol,df_s],axis=0).reset_index(drop=True)
                                    df_Filter  = pd.concat([df_Filter,df_s],axis=0).reset_index(drop=True)
                                    
                                    passedTime  = time.time()
                                    timerStop   = time.time()
                                    sofar       = round((passedTime - start)/60,1)
                                    scanTime    = round(timerStop - timerStart,1)
                                    present     = now()

                                    if NetProfit != 0:
                                        dataExists = "OK"
                                    else:
                                        dataExists = "-----"

                                    print(f"\n ---Finalize--- \n {df_s}")
                                    Discord_Stream(SymbolName, path.AvatarParam, f"{scanTime}s, {dataExists} -NEXT-")

                                    export_result("All",df_All)
                                    export_result("Symbol",df_Symbol)

                                #######         #######         #####################        #######         #######         
                                        #######         ########     [6]Set Alert    #######         #######         
                                #######         #######         #####################        #######         #######         
                try:
                    df_Filter = df_Filter.sort_values(by="NetProfit", ascending=False)
                    df_Filter.drop(df_Filter.loc[df_Filter['NetProfit']==0].index, inplace=True)
                    df_Filter.drop(df_Filter.loc[df_Filter['ProfitFactor']<=Filter_Finalize_ProfitFactor ].index, inplace=True)
                    df_Filter.drop(df_Filter.loc[df_Filter['SortinoRatio']<=Filter_Finalize_SortinoRatio].index, inplace=True)
                    df_Filter.reset_index(drop=True, inplace=True)

                    StrategyName  = df_Filter.iloc[0, 1]
                    SymbolName    = df_Filter.iloc[0, 2]
                    param_1       = int(df_Filter.iloc[0, 3])
                    param_2       = int(df_Filter.iloc[0, 4])
                    param_3       = int(df_Filter.iloc[0, 5])
                    param_4       = int(df_Filter.iloc[0, 6])
                    param_5       = int(df_Filter.iloc[0, 7])
                    Discord_Alert("Finalized!", path.AvatarStrategy, f"Congrats! {SymbolName} has Finalized!")
                except:
                    error_message = f"{SymbolName}: No one qualified Qualify."
                    print(error_message)
                    Discord_Alert("No Qualify", path.AvatarNoQualify, error_message)
                    break
                else:
                    export_result("Finalize",df_Filter)

                    df_Filter.drop_duplicates(subset='symbol', keep='first', inplace=True)

                    export_result("Activate",df_Filter)

                    browser.find_element(By.XPATH,value=path.halfBottomTab).click() 
                    browser.find_element(By.XPATH, value=path.deepHistory).click() 

                    browser.find_element(By.XPATH, value = '//*[@id="header-toolbar-symbol-search"]').click() #click_SearchBar
                    if check_exists_by_xpath(f'//div[2]/div[2]/div/div[.="{source}"]')==False:
                        browser.find_element(By.XPATH, value=path.SourceMenu).click()
                        browser.find_element(By.XPATH, value=(f'//div[15]/div[2]/div/div[2]/div[1][.="{source}"]')).click()
                    elem_Search  = browser.find_element(By.XPATH, value='//input[(@data-role="search")]')
                    elem_Search.clear()
                    elem_Search.send_keys(f"{SymbolName}")
                    browser.find_element(By.XPATH, value=f'//div[2]/div/span/em[.="{SymbolName}"]').click()

                    input_Param(1,param_1)
                    input_Param(2,param_2)
                    input_Param(3,param_3)
                    input_Param(4,param_4)
                    input_Param(5,param_5)
                    click_SubmitParam()

                    browser.find_element(By.XPATH, value=path.Alert).click() 
                    browser.find_element(By.XPATH, value=path.AlertConditionMenu).click()

                    elem_AlertMessage = browser.find_element(By.XPATH, value=path.AlertMessage)
                    elem_AlertMessage.send_keys(Keys.CONTROL,"a")
                    elem_AlertMessage.send_keys(Keys.BACK_SPACE)
                    elem_AlertMessage.send_keys("{{strategy.order.alert_message}}")

                    browser.find_element(By.XPATH, value=path.SubmitAlert).click()
                    Discord_Alert("Activation",path.AvatarSetup,f"Activation on {SymbolName}. {StrategyName}({param_1},{param_2})")
                    sleep(1.5)
                    browser.find_element(By.XPATH, value=path.deepHistory).click() 
                    browser.find_element(By.XPATH, value=path.openBottomTab).click() 
                    sleep(1.5)
            except:
                error_message = f"{SymbolName}: No one qualified Qualify."
                print(error_message)
                Discord_Alert("No Qualify", path.AvatarNoQualify, error_message)
    except exceptions.NoSuchElementException as e:
        error_message = f"Error occured at scanning process. reason: {e}"
        Discord_Alert("ERROR!!",path.AvatarFailed,error_message)
        print(f"ERROR!! {error_message}")
    else:
        end = time.time()
        runtime = end - start

        resultInfo = f"Mission Accomplished\nRUNTIME\n{round(runtime)}/sec \n{round(runtime/60)}/min \n{round(runtime/60/60)}/hour "
        print(scanInfo + resultInfo)

        Discord_Stream(f"Scan Successed!",path.AvatarComplete,f"{scanInfo}{resultInfo}")
        Discord_Alert(f"Scan Successed!",path.AvatarComplete,f"{scanInfo}{resultInfo}")
                
    sleep(10)
    browser.quit()

images = [
    "https://firebasestorage.googleapis.com/v0/b/docker-curriculum.appspot.com/o/catnip%2F0.gif?alt=media&token=0fff4b31-b3d8-44fb-be39-723f040e57fb",
]

@app.route("/home")
def index():
    url = random.choice(images)
    return render_template("index.html", url=url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
