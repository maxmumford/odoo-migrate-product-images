## Functionality

This script helps you migrate product images from one odoo instance to another. It will get the xml (external) IDs for each product in the source database, and if it finds a product in the target database with the same xml (external) ID, it will download the image from the image_medium field in the source database and upload it to the target database.

## Example Usage:

Execute the below command replacing the parameters as appropriate. The parameters prefixed with "source_" refer to the odoo instance that will export images, and the parameters prefixed with "target_" refer to the odoo instance that will import them.

    python ./migrate.py --source-database=SOURCE_DB --target-database=TARGET_DB --source-hostname=MYINSTANCE.odoo.com --target-hostname=MYINSTANCE.COM --source-username=USERNAME --source-password=PASSWORD --target-username=USERNAME --target-password=PASSWORD --source-saas true --target-product-model=product.template

### Notes:
If the --source-saas and --target-saas parameters are set to true, the protocol and port will be set automatically to work with the Odoo saas service.

Run the script with the --help parameter for more parameter information.

