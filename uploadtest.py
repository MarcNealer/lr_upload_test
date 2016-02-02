import requests
import simplejson
import sys, getopt
from requests_oauthlib import OAuth1
from datadiff import diff

# change these variables to match your required auth tokens
consumer_key = ''
consumer_secret = ''
oauth_token= 'node_sign_token'
oauth_token_secret = ''

def checkArgument(argv):
    try:
        opts, args = getopt.getopt(argv, "d:l:n:")
    except:
        print "uploadtest.py -d <document> -l <resource locator> -n <node>"
        print "Example: uploadtest.py -d test.json -l http://mysite.com -n http://sandbox.learningregstry.com"
        sys.exit(2)
    return dict(opts)
class UploadTest:
    def __init__(self):
        self.client = requests.Session()
        self.base =  simplejson.loads(open('base.json').read())
        self.auth = OAuth1(consumer_key,consumer_secret ,oauth_token,oauth_token_secret)
        self.client.headers={"content_type":"application/json"}
        self.document_id=False

    def loadDocument(self,document,url):
        doc = simplejson.loads(open(document).read())
        self.upload_doc=self.base
        self.upload_doc['resource_data']=doc
        self.upload_doc['resource_locator']=url
    def uploadToNode(self,upload_url):
        #upload to the node
        resp=self.client.post("%s/publish" % upload_url,simplejson.dumps({"documents":[self.upload_doc]}),verify=False,auth=self.auth)
        try:
            if resp.json()['document_results'][0]['OK']:
                print('Results uploaded')
                self.document_id=resp.json()['document_results'][0]['doc_ID']
                print('document Id: %s' % self.document_id)
            else:
                print('upload Failed')
        except:
            print('Upload Failed')

        # test reponse from the node
    def downloadFromNode(self,download_url):
        if self.document_id:
            dl_url="%sharvest/getrecord?request_id=%s&by_doc_ID=true" % (download_url,self.document_id)
            resp=self.client.get(dl_url,verify=False,auth=self.auth)
            if not self.upload_doc['resource_locator'] in resp.content:
                print('download mismatch on locator')
            else:
                print('locator found ok')
            testdata=resp.json()
            compare=diff(self.upload_doc['resource_data']['items'],testdata['getrecord']['record'][0]['resource_data']['resource_data']['items'])
            compare=set([x[0] for x in compare.diffs])

            if 'delete' in compare:
                print('missing data')
            else:
                print('resource data matched')

# get document from the node
# test against the uploaded data


if __name__ == '__main__':
    options = checkArgument(sys.argv[1:])
    upload  =UploadTest()
    upload.loadDocument(options['-d'],options['-l'])
    upload.uploadToNode(options['-n'])
    upload.downloadFromNode(options['-n'])
