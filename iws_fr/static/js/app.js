Sugar.extend();

function FeatureRequest(data) {
    this.user = ko.observable(data.user);
    this.client = ko.observable(data.client);
    this.identifier = ko.observable(data.identifier);
    this.title = ko.observable(data.title);
    this.description = ko.observable(data.description);
    this.priority = ko.observable(data.priority);
    this.targetDate = ko.observable(data.target_date);
    this.productAreas = ko.observable(data.product_areas);
    this.created = ko.observable(data.created);
    this.comments = ko.observable(data.comments);

    this.lastModified = ko.observable();

    ko.computed(function() {
        var that = this;
        $.getJSON(
            '/api/comment/' + this.comments().max('created').id,
            function (commentData) {
                var user = commentData.user;
                var date = new Date(commentData.created);

                that.lastModified({
                    'user': user,
                    'date': date,
                    'date_relative': date.relative()
                });
            }
        );
    }, this);
}

function FeatureRequestListViewModel() {
    var self = this;
    self.featureRequests = ko.observableArray([]);

    // Load initial data from the database.
    $.getJSON('/api/feature_request', function(allData) {
        console.log(allData);
        var mappedFRs = $.map(allData.objects, function(fr) {
            return new FeatureRequest(fr);
        });
        self.featureRequests(mappedFRs);
    });
}

ko.applyBindings(new FeatureRequestListViewModel());
