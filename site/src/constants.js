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

    static UPDATE_NUMBER_INPUT          = (
        `${Constants.BACKEND_URL}/update-number`);
    static UPDATE_RECOVERY_EMAIL_INPUT  = (
        `${Constants.BACKEND_URL}/update-recovery-email`);
    static UPDATE_PASSWORD_INPUT        = (
        `${Constants.BACKEND_URL}/update-password`);
    static UPDATE_USERNAME_INPUT        = (
        `${Constants.BACKEND_URL}/update-username`);
    static UPDATE_PROFILE_INPUT         = (
        `${Constants.BACKEND_URL}/update-profile`);

    static GET_WISPS_ENDPOINT   = `${Constants.BACKEND_URL}/get-wisps`;

    // width and height of virtual grid
    static VGRID_DIMENSION = 1000;
    // static VGRID_HEIGHT = 1000; 

    static AUTH_CODE_LENGTH = 6;
}

export default Constants;
