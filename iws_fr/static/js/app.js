// TODO: comments
Sugar.extend();

// Refresh data every so often..
//function ModelDataPoller() {
//    var INTERVAL = 5000;
//    var timeout = null;
//
//    var poll = function(endpoint) {
//        request = $.getJSON(endpoint);
//        request
//            .done(process)
//            .always(pollAgain)
//    };
//
//    var process = function(data) {
//        ko.mapping.fromJS(data.objects, viewModel);
//    }
//
//    var pollAgain = function() {
//
//    }
//};


//var data;
//
//$.getJSON('/api/feature_request', function(allData) {
//    data = allData.objects;
//});
//
//var featureRequest = ko.mapping.fromJS(data);
//
//ko.mapping.fromJS(data, viewModel);
//
//
//// ...
//var queryParams = JSON.stringify({
//    'order_by': [{'field': 'created', 'direction': 'desc'}],
//    'limit': 1,
//    'filter': [{'name': 'feature_request_id', 'op': '==', 'val': 1}]
//});
//$.getJSON('/api/comment',
//    {'q': queryParams},
//    function(data) { console.log(data); }
//);

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

        if (this.comments().length > 0) {
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
        } else {
            var date = new Date(that.created());

            that.lastModified({
                'user': that.user(),
                'date': date,
                'date_relative': date.relative()
            })
        }
    }, this);
}

// TODO: models for other ones,
// TODO: link them together on client-side here?
// TODO: polling for updates.
// TODO: gui! - finish display, then need edit + new + delete
// TODO: sort by priority
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
