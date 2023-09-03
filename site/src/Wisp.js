import React from "react";
import Constants from "./constants.js";

// React component for individual Wisp
class Wisp extends React.Component {
    render() {
        return (
            <div className="Wisp BoxShadow">
                <div className="WispUserBox">
                    <div className="WispUserProfile">
                        <img className="WispUserProfileImg BoxShadow" 
                        alt="user profile"
                        src={
                            (`${Constants.PROFILE_ENDPOINT}/` +
                            this.props.data["user_profile_uri"])
                        } />
                    </div>
                </div>
                <div className="WispTextBox">
                    <div className="WispUserName">
                        {this.props.data["user_username"]}
                    </div>
                    <div className="WispText">
                        {this.props.data["text"]}
                    </div>
                    { this.props.data["gif_uri"] !== "" ? 
                        <div className="WispGif">
                            <img className="WispImg" 
                            alt="wisp attachment"
                            src={
                                (`${Constants.GIF_ENDPOINT}/` +
                                this.props.data["gif_uri"])
                            } />
                        </div>
                    : <></> }
                </div>
            </div>
        );
    }
}

export default Wisp;
