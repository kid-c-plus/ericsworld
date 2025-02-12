"""
App views for HeartWizard related actions - changing the UI elements,
    getting the current UI set, and checking to see if the current user
    is the HeartWizard.
"""
from flask import request
import flask_login
import uuid
from sqlalchemy.exc import IntegrityError

from app import flaskapp, appconfig, db, constants

from app.models import *

@flaskapp.route("/get-ui", methods=["GET"])
def get_ui():
    """
    GET endpoint for checking the currently set UIConfig values.
    :return: 200 and {"font", "device", "color_palette"} dict
    """
    config = db.session.execute(
        db.select(UIConfig).order_by(
            UIConfig.set_time.desc()
        )
    ).scalar()
    
    # create default config if none is present
    if config:
        return config.to_dict(), 200
    else:
        #response = set_ui(appconfig["DEFAULT_UICONFIG"])
        response = (0, 200)
        return appconfig["DEFAULT_UICONFIG"], response[1]

@flaskapp.route("/set-ui", methods=["POST"])
def set_ui(overriding_config=None):
    """
    POST endpoint for setting UIConfig. Only accessible by the 
        HeartWizard.
    :param overriding_config: if provided, set the config with
        the provided values without checking the context of the 
        current user. This will only be provded when called locally,
        not as an HTTP request.
    :jsonparam font: new font to set
    :jsonparam device: URI for new device to set
    :jsonparam color_palette: identifier for new color palette to set
    :return: 200 if UIConfig is changed, 403 if user is not the 
        HeartWizard, 400 if bad request or unrecognized values
    """
    if overriding_config:
        font, device, color_palette = (
            overriding_config.get(key) for key in (
                "font", "device", "color_palette"
            )
        )
    else:
        # pass login check requirement on to check_heartwizard
        if (check_heartwizard()[1] == 401 or 
                not check_heartwizard()[0]["heartwizard"]):
            return {"error": "you are not the heartwizard"}, 403

        font, device, color_palette = (
            request.json.get(key) for key in (
                "font", "device", "color_palette"
            )
        )

    if not (font and font in appconfig["FONTS"] and
            device and device in appconfig["DEVICES"] and
            color_palette and 
            color_palette in appconfig["COLOR_PALETTES"]):
        return {"error": "malformed request"}, 404

    curr_config = db.session.execute(
        db.select(UIConfig)
    ).scalar()

    if curr_config:
        db.session.delete(curr_config)
        db.session.commit()

    config_added = False
    while not config_added:
        try:
            config = UIConfig(
                config_id=uuid.uuid1().hex,
                font=font, 
                device=device, 
                color_palette=color_palette
            )
            db.session.add(config)
            db.session.commit()
            config_added = True
        except IntegrityError:
            tries += 1
            if tries >= 3:
                return {
                    "error": "Unable to update config."
                }, 500

    return {"response": "ui updated"}, 200

@flaskapp.route("/check-heartwizard", methods=["GET"])
@flask_login.login_required
def check_heartwizard():
    """
    GET endpoint to check if the current user is the HeartWizard (i.e.
        has the highest HeartScore on the site).
    :return: 200 and {"heartwizard"} boolean dict
    """
    curr_user = flask_login.current_user

    heartwizard = db.session.execute(db.select(User).filter_by(
            status=constants.ACTIVE_USER
        ).order_by(
            User.heartscore.desc()
        )
    ).scalar()

    if heartwizard:
        # compare heartscores, so that ties can produce multiple Wizards
        return {
            "heartwizard": curr_user.heartscore == heartwizard.heartscore
        }, 200
    else:
        return {"error": "no users found"}, 404
