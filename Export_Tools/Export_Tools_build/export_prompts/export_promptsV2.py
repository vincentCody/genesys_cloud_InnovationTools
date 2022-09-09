import PureCloudPlatformClientV2
from PureCloudPlatformClientV2.rest import ApiException
import os
import argparse
import json
import requests
# Create the parser
parser = argparse.ArgumentParser(add_help=False)
# Add an argument
parser.add_argument('--clientId', type=str, required=True, help="Org's ClientId")
parser.add_argument('--clientSecret', type=str, required=True, help="Org's ClientSecret")
parser.add_argument('--region', type=str, required=True, help="Org's Region:'us_east_1','us_west_1','ap_southeast_2','ap_northeast_1','eu_central_1','us_west_2','ca_central_1','ap_northeast_2','eu_west_2','ap_south_1','us_east_2','sa_east_1'")
parser.add_argument('--outputPATH', type=str, required=True, help="Export Audio files location:'./output'")
# Parse the argument
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help="To execute this exe file : .\export_promptsV2.exe --clientId <clientID> --clientSecret <clientSecret> --region <region> --outputPATH ./output")
args = parser.parse_args()
prompt_content = []
header = ['Name','Type','Description']

if args.region:
    print("ClientID : "+args.clientId)
    print("ClientSecret : "+args.clientSecret)
    print("Region : "+args.region)
    print("OUTPUT_PATH : "+args.outputPATH)
    print("===================START======================")
    S_region = PureCloudPlatformClientV2.PureCloudRegionHosts[args.region]
    S_CLIENTID=args.clientId
    S_CLIENTSECRET=args.clientSecret
    OUTPUT_PATH = args.outputPATH
    S_ARCHY_location=S_region.value.replace("https://api.","") #remove prefix --> https://developer.genesys.cloud/forum/t/platformclient-purecloudregionhosts-us-east-1-returns-incorrect-url/14354/2
    cwd = os.getcwd()


    
    OUTPUT_FILENAME=OUTPUT_PATH+"/import_user_promts_file_"+S_CLIENTID+".csv"


    
    def CheckORCreateDir(OUTPUT_PATH):
        print("Checking OUTPUT dir :" + OUTPUT_PATH)
        MYDIR = (OUTPUT_PATH)
        CHECK_FOLDER = os.path.isdir(MYDIR)
        if not CHECK_FOLDER:
            os.makedirs(MYDIR)
            print("Created folder : ", MYDIR)
        else:
            print(MYDIR, "Folder already exists.")

    
    def delfile(file) :
        #print("Checking old file : "+ file)
        if os.path.exists(file):
            os.remove(file)
            print("Found old file and removed : "+ file)
    

    def downloadWAV(filename,link):
        print("Downloading audio ")
        x = requests.get(link)

        with open(filename, 'wb') as f:
            f.write(x.content)
            f.close
        print("Done downloading audio file : "+filename)



    def GC_apiclient(clientId,clientSecret,region):
        PureCloudPlatformClientV2.configuration.host = region.get_api_host()
        apiclient = PureCloudPlatformClientV2.api_client.ApiClient().get_client_credentials_token(clientId,clientSecret)
        return apiclient

    def getPrompts_list(page_number):
        page_size = 25 # int | Page size (optional) (default to 25)
        sort_by = 'id' # str | Sort by (optional) (default to 'id')
        sort_order = 'asc' # str | Sort order (optional) (default to 'asc')
        try:
            # Get a pageable list of flows, filtered by query parameters
            api_response = architectApi.get_architect_prompts(
                                                                page_number=page_number, 
                                                                page_size=page_size, 
                                                                sort_by=sort_by, 
                                                                sort_order=sort_order
                                                                )
            #print(api_response)
            return api_response
        except ApiException as e:
            print("Exception when calling GetFlowsRequest->get_flows: %s\n" % e)

    apiclient=GC_apiclient(S_CLIENTID,S_CLIENTSECRET,S_region)

    architectApi = PureCloudPlatformClientV2.ArchitectApi(apiclient)
    #page_number = 1 # int | Page number (optional) (default to 1)
    print("Python SDK retrieving Org Flows : ")
    data = getPrompts_list(0)
    print("Number of Pages : "+ str(data.page_count))
    print("Number Prompts per page : "+str(data.page_size))
    print("Total Prompts : "+str(data.total))
    #print(data)

    print("==============Listing Prompts==================")
    exec_cmd = []
    count = 0 
    for y in range(data.page_count):
        data = getPrompts_list(y+1)
        for x in data.entities:
            count = count+1
            print(str(count) +" PromptName :"+ str(x.name))
            

            name = x.name
            description=''
            #print(x.description)
            #print(x.name)
            data = {}

            data['Name'] = name
            data['Type'] = 'user'

            if(x.description != None):
                    description = x.description
            data['Description'] = description
            
            for i in x.resources : 
                #if hasattr(i,'media_uri'):
                #print(name_architect)  
                # i.language = i.id   
                # i.tts_string = i.tts_string
                # 
                #print(i)
                language=''
                if(i.id != None):
                    language = i.id 

                tts_string=''
                if(i.tts_string != None):
                    tts_string = i.tts_string

                language_default=''
                if(i.language_default != None):
                    language_default = i.language_default      
            
                media_uri = ''
                media_filename = ''
                if(i.media_uri !=None ):
                    media_uri = i.media_uri
                    media_filename = S_CLIENTID+"_"+name+"_"+language+".wav"
    
                #print(language)
                #print(tts_string)
                #print(language_default)
                #print (media_uri)
                
                data['tts_'+language] = tts_string
                data['audio_'+language] = media_filename
                data['audio_'+language+'_link'] = media_uri
                #Adding header columns for prompt csv
                if 'tts_'+language not in header and 'audio_'+language not in header:
                        header.append('tts_'+language)
                        header.append('audio_'+language)
                        
            json_data = json.dumps(data)
            #print(json_data)
            prompt_content.append(json_data)
            #print("Done")
                

    print("Done processing "+str(count)+ " prompts. \n")

    CheckORCreateDir(OUTPUT_PATH)

    #creating CSV file 
    print("Writing file : "+ OUTPUT_FILENAME)

    delfile(OUTPUT_FILENAME)
    
    f = open(OUTPUT_FILENAME, "w",encoding='utf-8')
    head = ''
    for column_name in header:
        column_csv="\""+column_name+"\""
        head +=","+column_csv
    head=head[1:]
    f.write(head+"\n")
    for val in prompt_content:
        read_json=json.loads(val)
        #print(read_json)
        line = ''
        column_val=''
            
        for x in header:
            if(x in read_json):
                column_val = ("\""+str(read_json[x])+"\"")
                #print(str(read_json[x]))
            else:
                #print(x + " -")
                column_val = ''
            
            line +=","+column_val
        line = line[1:] 
        #print(line)
        f.write(line+"\n")
    f.close()

    print("Finish populating user_prompts_file : "+OUTPUT_FILENAME)
    print("==============Downloading audio files==================")
    
    for val in prompt_content:
        read_json=json.loads(val)
        #print(read_json)

        getAudioName = ''
        getAudioLink = ''
        for val2 in read_json : 
            #print(val )
            if('audio_' in val2 and '_link' not in val2):
                #print(val2)
                if(read_json[val2] !=''):
                    #print(read_json[val2])
                    getAudioName = read_json[val2]
                    print("Downloading audio file : "+ getAudioName)
                    link = read_json[val2+'_link']
                    print("Downloading link : "+ link)
                    PATH_AudioName=OUTPUT_PATH+"/"+getAudioName
                    downloadWAV(PATH_AudioName,link)
                    print("Done Downloading")
    print("===================END======================")