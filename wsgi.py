from iws_fr import app

app.config.from_object('config.ProductionConfig')
import iws_fr.views
app.run()
