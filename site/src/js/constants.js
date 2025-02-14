// Constant definitions
class Constants {
    static BACKEND_URL          = "https://localhost:5000";

    static CSRF_ENDPOINT        = `${Constants.BACKEND_URL}/hai`;

    static PROFILE_ENDPOINT     = (
        `${Constants.BACKEND_URL}/static/profiles`);
    static GIF_ENDPOINT     = (
        `${Constants.BACKEND_URL}/static/gifs`);
    static ASSET_ENDPOINT     = (
        `${Constants.BACKEND_URL}/static/assets`);

    static LOGIN_ENDPOINT           = `${Constants.BACKEND_URL}/login`;
    static LOGOUT_ENDPOINT          = (
        `${Constants.BACKEND_URL}/logout`);
    static ACCOUNT_INFO_ENDPOINT    = (
        `${Constants.BACKEND_URL}/get-account-info`);

    static UPDATE_PHONE_NUMBER_ENDPOINT     = (
        `${Constants.BACKEND_URL}/update-number`);
    static UPDATE_RECOVERY_EMAIL_ENDPOINT   = (
        `${Constants.BACKEND_URL}/update-recovery-email`);
    static UPDATE_PASSWORD_ENDPOINT         = (
        `${Constants.BACKEND_URL}/update-password`);
    static UPDATE_USERNAME_ENDPOINT         = (
        `${Constants.BACKEND_URL}/update-username`);
    static UPDATE_PROFILE_ENDPOINT          = (
        `${Constants.BACKEND_URL}/update-profile`);
    static GET_PROFILES_ENDPOINT            = (
        `${Constants.BACKEND_URL}/get-profiles`);

    static CHECK_USERNAME_ENDPOINT  = (
        `${Constants.BACKEND_URL}/check-username`);
    
    static GET_WISPS_ENDPOINT           = (
        `${Constants.BACKEND_URL}/get-wisps`);
    static POST_WISP_ENDPOINT           = (
        `${Constants.BACKEND_URL}/post-wisp`);
    static HEART_WISP_ENDPOINT          = (
        `${Constants.BACKEND_URL}/heart-wisp`);
    static UNHEART_WISP_ENDPOINT        = (
        `${Constants.BACKEND_URL}/unheart-wisp`);
    static GET_HEARTED_WISPS_ENDPONT    = (
        `${Constants.BACKEND_URL}/hearted-wisps`);

    static GIF_SEARCH_ENDPOINT  = (
        `${Constants.BACKEND_URL}/gif-search`);

    // width and height of virtual grid
    static VGRID_DIMENSION = 1000;
    // static VGRID_HEIGHT = 1000; 

    static AUTH_CODE_LENGTH = 6;

    static MIN_USERNAME_LENGTH  = 3;
    static MAX_USERNAME_LENGTH  = 12;

    static MAX_EMAIL_LENGTH  = 320;

    static MAX_WISP_LENGTH      = 140;

    // line height, in vpixels, of wisp edit pane (necessary for 
    // scroll management
    static WISP_EDIT_LINE_HEIGHT    = 50;

    // duration for displaying notifications
    static NOTIFICATION_DURATION    = 1000;

    // time to allow Deactivated animation to play before
    // removing div
    static DEACTIVATION_DURATION    = 500;

    // Keycodes
    static ENTER_KEY    = 13;
    static ESCAPE_KEY   = 27;
}

export default Constants;
