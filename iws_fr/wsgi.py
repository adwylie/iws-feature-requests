from iws_fr import app
from .config import ProductionConfig

app.config.from_object(ProductionConfig)

import iws_fr.views
