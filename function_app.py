import logging
import os
import sys
import sendgrid
import sendgrid.helpers.mail
import azure.functions as func
import alcoholFinder as alcolholFinder

app = func.FunctionApp()
run_on_startup = 'pydevd' in sys.modules # Check if the debugger is attached

@app.function_name(name="findAlcoholScheduled")
@app.timer_trigger(schedule="0 30 16 * * *", arg_name="myTimer", run_on_startup=run_on_startup, use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    itemCode = os.environ['ITEM_CODE']
    origin = os.environ['ORIGIN_ADDRESS']

    alcolholFinder.establishSession()
    locations = alcolholFinder.queryProduct(itemCode)
    if (len(locations) == 0):
        logging.info("No results found")
        sendEmail("No results found")
        return
    
    locationsWithDistances = alcolholFinder.getDistanceMatrix(origin, locations)
    email_content = "Here are the locations with the product and their distances:\n\n"
    for location in locationsWithDistances:
        email_content += f"Address: {location.address}\n"
        email_content += f"Travel time: {location.timeInSeconds / 60} min\n"
        email_content += f"Stock: {location.quantity}\n"
        email_content += "-" * 40 + "\n"
    sendEmail(email_content)

def sendEmail(email_content):
    sendgridClient = sendgrid.SendGridAPIClient(api_key=os.environ['SENDGRID_API_KEY'])
    fromAddress = sendgrid.helpers.mail.Email(os.environ['SENDGRID_FROM_ADDRESS'])
    toAddress = sendgrid.helpers.mail.To(os.environ['SENDGRID_TO_ADDRESS'])
    subject = "Alcohol Finder Results"
    content = sendgrid.helpers.mail.Content("text/plain", email_content)
    mail = sendgrid.helpers.mail.Mail(fromAddress, toAddress, subject, content)
    response = sendgridClient.client.mail.send.post(request_body=mail.get())
    logging.info(f"Email response status code: {response.status_code}")