import PureCloudPlatformClientV2
from PureCloudPlatformClientV2.rest import ApiException
import os
import argparse
# Create the parser
parser = argparse.ArgumentParser(add_help=False)
# Add an argument
parser.add_argument('--clientId', type=str, required=True, help="Org's ClientId")
parser.add_argument('--clientSecret', type=str, required=True, help="Org's ClientSecret")
parser.add_argument('--region', type=str, required=True, help="Org's Region:'us_east_1','us_west_1','ap_southeast_2','ap_northeast_1','eu_central_1','us_west_2','ca_central_1','ap_northeast_2','eu_west_2','ap_south_1','us_east_2','sa_east_1'")
parser.add_argument('--archyPATH', type=str, required=True, help="WINDOWS:'./archy-win/archy.bat', LINUX :'./archy-linux/archy', MACOS:'./archy-macos/archy'")
parser.add_argument('--outputPATH', type=str, required=True, help="Export YAML location:'./output'")
# Parse the argument
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help="To execute this exe file : .\export_flows.exe --clientId <clientID> --clientSecret <clientSecret> --region <region> --archyPATH ./archy-win/archy.bat --outputPATH ./output")
args = parser.parse_args()


if args.region:
    print("ClientID : "+args.clientId)
    print("ClientSecret : "+args.clientSecret)
    print("Region : "+args.region)
    print("ARCHY_PATH : "+args.archyPATH)
    print("OUTPUT_PATH : "+args.outputPATH)
    print("===================START======================")
    S_region = PureCloudPlatformClientV2.PureCloudRegionHosts[args.region]
    S_CLIENTID=args.clientId
    S_CLIENTSECRET=args.clientSecret
    ARCHY_PATH= args.archyPATH
    OUTPUT_PATH = args.outputPATH
    S_ARCHY_location=S_region.value.replace("https://api.","") #remove prefix --> https://developer.genesys.cloud/forum/t/platformclient-purecloudregionhosts-us-east-1-returns-incorrect-url/14354/2
    cwd = os.getcwd()


    def GC_apiclient(clientId,clientSecret,region):
        PureCloudPlatformClientV2.configuration.host = region.get_api_host()
        apiclient = PureCloudPlatformClientV2.api_client.ApiClient().get_client_credentials_token(clientId,clientSecret)
        return apiclient

    def getFlows_list(page_number):
        page_size = 25 # int | Page size (optional) (default to 25)
        sort_by = 'id' # str | Sort by (optional) (default to 'id')
        sort_order = 'asc' # str | Sort order (optional) (default to 'asc')
        deleted = False# bool | Include deleted (optional) (default to False)
        include_schemas = False # bool | Include variable schemas (optional) (default to False)
        try:
            # Get a pageable list of flows, filtered by query parameters
            api_response = architectApi.get_flows( 
                page_number=page_number, 
                page_size=page_size, 
                sort_by=sort_by, 
                sort_order=sort_order, 
                deleted=deleted, 
                include_schemas=include_schemas
                )
            #print(api_response)
            return api_response
        except ApiException as e:
            print("Exception when calling GetFlowsRequest->get_flows: %s\n" % e)

    def TransformArchyFlow(clientId,clientSecret,exportType,
                            debug,location,outputDir,flowType,flowName):
        #print ("Creating Archy Flow \n")
        cmd = cwd+'/'+ARCHY_PATH+' export --clientId {} --clientSecret {} --exportType {} --debug {} --location {} --outputDir {} --flowType {} --flowName {}'.format(clientId,clientSecret,exportType,debug,location,cwd+"/"+outputDir,flowType,"\""+flowName+"\"" )
        return cmd


    apiclient=GC_apiclient(S_CLIENTID,S_CLIENTSECRET,S_region)

    architectApi = PureCloudPlatformClientV2.ArchitectApi(apiclient)
    #page_number = 1 # int | Page number (optional) (default to 1)
    print("Python SDK retrieving Org Flows : ")
    data = getFlows_list(0)
    print("Number of Pages : "+ str(data.page_count))
    print("Number Flows per page : "+str(data.page_size))
    print("Total Flows : "+str(data.total))
    print("==============Listing Flows==================")
    exec_cmd = []
    count = 0 
    for y in range(data.page_count):
        data = getFlows_list(y+1)
        for x in data.entities:
            count = count+1
            print(str(count) +": FlowType :"+ str(x.type) +" , FlowName :"+ str(x.name))
            cmd_archy=TransformArchyFlow(S_CLIENTID,S_CLIENTSECRET,'yaml',
                                    False,S_ARCHY_location,OUTPUT_PATH+"/"+x.type,x.type.lower(),x.name)
            exec_cmd.append(cmd_archy)
    print("==============Exporting Flows==================")
    for z in exec_cmd:
        print("Archy export cmd : " + z)
        os.system(z)
    print("===================END======================")