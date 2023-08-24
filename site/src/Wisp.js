import React from "react";
import Constants from "./constants.js";

// React component for individual Wisp
class Wisp extends React.Component {
    constructor(props) {
        super(props);
        console.log(this.props);
    }

    render() {
        return (
            <div className="Wisp">
                <div className="WispUserBox">
                    <div className="WispUserProfile">
                        <img className="WispUserProfileImg" src={
                            `gifs/${this.props.data["user_profile_uri"]}`
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
                    { this.props.data["gif_uri"] != "" ? 
                        <div className="WispGif">
                            <img className="WispImg" src={
                                `gifs/${this.props.data["gif_uri"]}`
                            } />
                        </div>
                    : <></> }
                </div>
            </div>
        );
    }
}

export default Wisp;
