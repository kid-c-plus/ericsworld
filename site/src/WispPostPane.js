import React from "react";
import Constants from "./constants.js";
import Wisp from "./Wisp.js";

// Root component for Wisp creation pane
class WispPostPane extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            // Wisp component currently being edited
            // Right now, either "text" or "gif"
            focus:  "text",

            text:       "",
            gifUri:     ""
        }

    }

    render() {
        let editFocusElem = </>;
        if (this.state.focus === "text") {
            editFocusElem = (
                <div id="WispTextInputContainer"> 
                    <input type="text" id="WispTextInput"
                        name="WispTextInput" className="TextInput"
                        maxLength={`${constants.MAX_WISP_LENGTH}`}
                        value={this.state.text}
                        onChange={changeEvent => this.setState({
                            text: changeEvent.target.value})}
                    />
                </div>
            );
        } else if (this.state.focus === "gif") {
            editFocusElem = <GIFSearchSubpane selectGif={
                gifUri => this.setState({
                    gifUri: gifUri,
                    focus:  "text"
                })}
            />;
        }
        return (
            <div id="WispPostPane">
                <div id="EditSubpane">
                    <div id="TextSelectButton"
                            className={"WispEditSelectButton" +
                            (this.state.focus === "text" ? 
                            " selected" : "")}>
                        text
                    </div>
                    {editFocusElem}
                    <div id="TextSelectButton"
                            className={"GIFEditSelectButton" +
                            (this.state.focus === "gif" ? 
                            " selected" : "")}>
                        gif
                    </div>
                </div>
                <div className="FormElement">
                    <div className="FormButton BoxShadow" onClick={
                            this.post.bind(this)}>
                        send wisp 
                    </div>
                </div>
            </div>
        );

class GIFSearchSubpane extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            gifSearch:  "",
            gifUris:    []
        }
    }

    render() {
        let gifImgs = this.state.gifUris.map(gifUri => (
            <img className="GIFSearchImg" alt="gif search result"
                key=gifUri
                src={`${Constants.GIF_ENDPOINT}/${gifUri}`} />
        ));
        return (
            <div id="GIFSearchSubpane">
                <div id="GIFSearchBar">
                    <input type="text" id="GIFSearchInput"
                        name="GIFSearchInput"
                        className="TextInput"
                        value={this.state.gifSearch}
                        onChange={changeEvent => this.setState({
                            gifSearch: changeEvent.target.value})}
                    />
                    <div id="GIFSearchButton" onClick={
                            this.searchGifs.bind(this)}>
                        search
                    </div>
                </div>
                <div id="GIFSearchResultsSubpane">
                    {gifImgs}
                </div>
            </div>
        );
    }
};

export default WispPostPane;
