// Constant definitions
class Constants {
    static BACKEND_URL          = "http://localhost:5000";
    static CSRF_ENDPOINT        = `${Constants.BACKEND_URL}/hai`;
    static GET_WISPS_ENDPOINT   = `${Constants.BACKEND_URL}/get-wisps`;

    // width and height of virtual grid
    static VGRID_DIMENSION = 1000;
    // static VGRID_HEIGHT = 1000; 
}

export default Constants;
