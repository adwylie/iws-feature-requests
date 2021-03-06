var timeout;
var pollingRate = 2000;

// TODO: Improve UX for client filtering.
function FeatureRequestsPage(data) {
    var self = this;

    self.featureRequests = ko.observableArray();

    ko.mapping.fromJS(data, FeatureRequestsPage.mapping, self);

    var updatePriority = function (featureRequest, priority) {
        // Perform an ajax request to update the priority value.
        $.ajax(
            '/api/feature_request/' + featureRequest.id(),
            {
                contentType: 'application/json;',
                method: 'PATCH',
                data: JSON.stringify({ 'priority': priority }),
                success: function () {
                    // On success reset the timeout so that new/ data is
                    // fetched immediately.
                    clearTimeout(timeout);
                    updateFeatureRequests();
                }
            }
        );
    };

    self.incrementPriority = function (featureRequest) {
        // TODO: Fake action client-side?
        updatePriority(featureRequest, featureRequest.priority() + 1);
    };

    self.decrementPriority = function (featureRequest) {
        updatePriority(featureRequest, featureRequest.priority() - 1);
    };

    self.filtering = ko.observable(false);
    self.filteredByClient = ko.observable();

    self.filterByClient = function (featureRequest) {
        self.filteredByClient(featureRequest.client());
        self.filtering(true);
    };

    ko.mapping.fromJS(data, FeatureRequestsPage.mapping, self);
}
FeatureRequestsPage.mapping = {
    featureRequests: {
        create: function (options) {
            return new FeatureRequest(options.data);
        },
        key: function (data) {
            return ko.utils.unwrapObservable(data.id);
        }
    }
};


var featureRequests = new FeatureRequestsPage({ featureRequests: []});
ko.applyBindings(featureRequests);


var updateFeatureRequests = function () {
    var callback = function(data) {
        ko.mapping.fromJS({ featureRequests: data.objects }, featureRequests);
        timeout = setTimeout(updateFeatureRequests, pollingRate);
    };

    var queryParams = JSON.stringify({
       'order_by': [
           {'field': 'client_id', 'direction': 'asc'},
           {'field': 'priority', 'direction': 'asc'}
       ]
    });
    $.getJSON('/api/feature_request', {'q': queryParams}, callback);
};

updateFeatureRequests();
