import React from "react";
import PhoneInput from 'react-phone-input-2';

import Constants from "./constants.js";

class ProfileUpdateSubpane extends React.Component {
    constructor(props) {
        super(props);
        
        this.state = {
            folders:    [],
            profiles:   [],

            selectedFolder:     null,

            highlightedFolderIndex:     0,
            highlightedProfileIndex:    0
        }

        fetch(
            Constants.GET_PROFILES_ENDPOINT,
            {
                credentials:    "include"
            }
        ).then(response => response.json())
        .then(folderResp => {
            this.setState({folders: folderResp['folders']})
        }).catch(error => {
            this.setState({folders: []})
            console.log(error);
        });
    }

    goBack(domEvent) {
        if (this.state.selectedFolder == null) {
            this.props.cancel();
        } else {
            this.setState({
                selectedFolder: null,
                profiles:       []
            });
        }
    }
    
    selectFolder(folder) {
        this.setState({selectedFolder: folder});
        let params = new URLSearchParams();
        params.append("folder", folder);
        fetch(
            `${Constants.GET_PROFILES_ENDPOINT}?${params}`, {
                credentials: "include"
        }).then(response => response.json())
        .then(profileResp => {
            this.setState({profiles: profileResp['profiles']})
        }).catch(error => {
            console.log(error);
        });
    }
    
    render() {
        let content = <></>;
        if (this.state.selectedFolder == null) {
            let folders = []
            if (this.state.folders.length > 0) {
                folders = this.state.folders.map(folder => (
                    <div className="ProfileFolder"
                        key={`profile-folder-${folder}`}
                        onClick={domEvent => this.selectFolder.bind(
                            this, folder)}>
                        <img alt={`${folder} folder`}
                            src="assets/folder.png"
                            className="FolderImg" />
                        <span className="caption">
                            {folder}
                        </span>
                    </div>
                ));
            } else {
                folders = (
                    <div className="GridLoadingMsg">
                        loading...
                    </div>
                );
            }
            content = (
                <div id="ProfileFolderContainer"
                    className="GridItemContainer">
                    {folders}
                </div>
            );
        } else {
            let profiles = []
            if (this.state.profiles.length > 0) {
                profiles = this.state.profiles.map(
                    profileUri => (
                        <img alt="profile option"
                            key={`profile-option-${profileUri}`}
                            className="ProfileImg"
                            onClick={this.props.updateProfile.bind(
                                this, profileUri)} />
                ));
            } else {
                profiles = (
                    <div className="GridLoadingMsg">
                        loading...
                    </div>
                );
            }

            content = (
                <div id="ProfileImgContainer">
                    {profiles}
                </div>
            );
        }

        return (
            <div id="ProfileUpdateSubpane" 
                className="Subpane ContentButtonContainer">
                {content}
                <div className="FormElement HorizontalContainer">
                    <div className="FormButton BoxShadow"
                        onClick={this.goBack.bind(this)}>
                        {this.state.selectedFolder == null ?
                            "cancel" : "back"}
                    </div>
                </div>
            </div>
        );
    }
}

export default ProfileUpdateSubpane;
