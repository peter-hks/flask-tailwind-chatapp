# Azure OpenAI Notes

To ssh into linux machine, first download the .pem file provided during deployment and login:
~~~
ssh -i <path to the .pem file> username@<ipaddress of the VM>
~~~

Example of instantiating openai model with azure in python (a couple slightly different settings required then locally running) https://github.com/Azure-Samples/openai/blob/main/Basic_Samples/Chat/basic_chatcompletions_example_sdk.ipynb

~~~
# Setting up the deployment name
chatgpt_model_name = config_details['CHATGPT_MODEL']

# This is set to `azure`
openai.api_type = "azure"

# The API key for your Azure OpenAI resource.
openai.api_key = os.getenv("OPENAI_API_KEY")

# The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
openai.api_base = config_details['OPENAI_API_BASE']

# Currently Chat Completion API have the following versions available: 2023-03-15-preview
openai.api_version = config_details['OPENAI_API_VERSION']
~~~

https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#model-summary-table-and-region-availability




