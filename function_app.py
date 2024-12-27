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
    itemCodes = os.environ['ITEM_CODES'].split(",")
    origin = os.environ['ORIGIN_ADDRESS']

    for itemCode in itemCodes:
        alcolholFinder.establishSession()
        findAlcohol(origin, itemCode)

def findAlcohol(origin: str, itemCode: str) -> None:
    product = alcolholFinder.queryProduct(itemCode)
    if (len(product.locations) == 0):
        logging.info(f"No results found for {itemCode}")
        return

    locationsWithDistances = alcolholFinder.getDistanceMatrix(origin, product.locations)

    # Skip locations that are more than 30 min away
    locationsWithDistances = list(filter(lambda x: x.timeInSeconds < 1800, locationsWithDistances))
    if (len(locationsWithDistances) == 0):
        logging.info(f"No locations found within 30 min for {product.name}")
        return

    email_content = f"Here are the locations with {product.name} and their distances:\n\n"
    for location in locationsWithDistances:
        email_content += f"{location.address}\n"
        email_content += f"{location.city}, OR {location.zip}\n"
        email_content += f"Travel time: {round(location.timeInSeconds / 60, 1)} min\n"
        email_content += f"Travel time w/ traffic: {round(location.timeWithTrafficInSeconds / 60, 1)} min\n"
        email_content += f"Stock: {location.quantity}\n"
        email_content += f"Phone: {location.phoneNumber}\n"
        email_content += "-" * 40 + "\n"
    sendEmail(product.name, email_content)

def sendEmail(subject: str, email_content: str) -> None:
    sendgridClient = sendgrid.SendGridAPIClient(api_key=os.environ['SENDGRID_API_KEY'])
    fromAddress = sendgrid.helpers.mail.Email(os.environ['SENDGRID_FROM_ADDRESS'])
    toAddress = sendgrid.helpers.mail.To(os.environ['SENDGRID_TO_ADDRESS'])
    subject = f"Alcohol Finder Results: {subject}"
    content = sendgrid.helpers.mail.Content("text/plain", email_content)
    mail = sendgrid.helpers.mail.Mail(fromAddress, toAddress, subject, content)
    response = sendgridClient.client.mail.send.post(request_body=mail.get())
    logging.info(f"Email response status code: {response.status_code}")