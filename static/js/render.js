Render = function() {
    //templates
    this.renderPrefix = 'render_';

    this.templates = {
        render_diff :''
    };

    //main stuff
    this.getRender = function() {
        return this.renderType;
    }

    this.setRender = function(renderType) {
        this.renderType = renderType;
    }

    /**
     * Checks if render has defined template
     * @return {Boolean}
     */
    this.renderHasTemplate = function() {
        if ( this.templates.hasOwnProperty(this.renderPrefix + this.getRender()) ){
            return true;
        }
        return false;
    }

    /**
     * Returns current render template
     * @return {*}
     */
    this.getRenderTemplate  = function() {
        return this.templates[ this.renderPrefix + this.getRender() ];
    }


    this.doRender = function(jsonData) {
        if ( this.renderHasTemplate() ) {
            return (
                Mustache.render(
                    this.getRenderTemplate(),
                    jsonData
                )
                );
        }
        throw 'no template for render '+ this.getRender();
    }

    this.sortObjects = function(jsonData, sortKey) {

    }

}