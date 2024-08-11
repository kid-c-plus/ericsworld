// Constant definitions
class Constants {
    static BACKEND_URL          = "https://localhost:5000";

    static CSRF_ENDPOINT        = `${Constants.BACKEND_URL}/hai`;

    static PROFILE_ENDPOINT     = (
        `${Constants.BACKEND_URL}/static/profiles`);
    static GIF_ENDPOINT     = (
        `${Constants.BACKEND_URL}/static/gifs`);
        
    
    static LOGIN_ENDPOINT           = `${Constants.BACKEND_URL}/login`;
    static LOGOUT_ENDPOINT          = (
        `${Constants.BACKEND_URL}/logout`);
    static ACCOUNT_INFO_ENDPOINT    = (
        `${Constants.BACKEND_URL}/get-account-info`);

    static UPDATE_NUMBER_ENDPOINT          = (
        `${Constants.BACKEND_URL}/update-number`);
    static UPDATE_RECOVERY_EMAIL_ENDPOINT  = (
        `${Constants.BACKEND_URL}/update-recovery-email`);
    static UPDATE_PASSWORD_ENDPOINT        = (
        `${Constants.BACKEND_URL}/update-password`);
    static UPDATE_USERNAME_ENDPOINT        = (
        `${Constants.BACKEND_URL}/update-username`);
    static UPDATE_PROFILE_ENDPOINT         = (
        `${Constants.BACKEND_URL}/update-profile`);

    static CHECK_USERNAME_ENDPOINT  = (
        `${Constants.BACKEND_URL}/check-username`);
    
    static GET_WISPS_ENDPOINT   = `${Constants.BACKEND_URL}/get-wisps`;

    // width and height of virtual grid
    static VGRID_DIMENSION = 1000;
    // static VGRID_HEIGHT = 1000; 

    static AUTH_CODE_LENGTH = 6;

    static MIN_USERNAME_LENGTH  = 3;
    static MAX_USERNAME_LENGTH  = 12;
}

export default Constants;
