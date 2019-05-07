var myApp = angular.module('psApp', []);

myApp.controller('sls', function($scope, $http) {

    $scope.mplist = [];
    $scope.full_mplist = [];
    $scope.communities = [];
    $scope.community = "";
    $scope.tools = [];
    $scope.tool = "";


    $scope.schedule_repeat_options = ["PT2M", "PT5M", "PT30M", "PT60M"]
    $scope.schedule_repeat = "PT5M"

    $scope.schedule_slip_options = ["PT2M", "PT5M", "PT10M"]
    $scope.schedule_slip = "PT5M"

    $scope.schedule_until_options = ["10m", "1h", "1d"]
    $scope.schedule_until = "1h"

    $scope.source = "";
    $scope.destination = "";

    // latency options
    $scope.packet_count_options = [10, 20, 50, 100]
    $scope.packet_count = 10

    // TODO: more supported options

    // throughput options
    $scope.duration_options = ["PT10S", "PT30S", "PT1M"]
    $scope.duration = "PT30S"

    $scope.interval_options = ["PT5S", "PT10S", "PT30S"]
    $scope.interval = "PT5S"
    // test_spec = {
    //     "schema": 1,
    //     "source": test_params["source"],
    //     "dest": test_params["destination"],
    //     "duration": "PT%sS" % test_params.get("duration", "30"),
    //     "interval": "PT%sS" % test_params.get("interval", "6")
    // }

    $http({
        method: 'GET',
        url: window.location.origin + "/sls/mplist"
    }).then(
        function(rsp) {
            $scope.mplist = rsp.data.map(obj => ({ ...obj, show: true }));
        },
        function(rsp) {$scope.mplist = ['error']}
    );

    $http({
        method: 'GET',
        url: window.location.origin + "/sls/mptools"
    }).then(
        function(rsp) {
            $scope.tools = rsp.data;
            $scope.tools.unshift("");  // filter disable option
        },
        function(rsp) {$scope.tools = ['error']}
    );

    $http({
        method: 'GET',
        url: window.location.origin + "/sls/mpcommunities"
    }).then(
        function(rsp) {
            $scope.communities = rsp.data;
            $scope.communities.unshift("");  // filter disable option
        },
        function(rsp) {$scope.communities = ['error']}
    );

    function hide(mp) {
        if ($scope.tool && !mp.tools.includes($scope.tool)) {
            return true;
        }
        if ($scope.community && !mp.communities.includes($scope.community)) {
            return true;
        }
        return false;
    }

    $scope.update_filter = function() {
        $scope.mplist.forEach(
            function(v, i) {
                $scope.mplist[i].show = !hide($scope.mplist[i])
            }
        )
    }

    $scope.show_latency_parameters = function() {
        return ['owamp', 'owping', 'twamp', 'twping'].includes($scope.tool)
    }

    $scope.show_throughput_parameters = function() {
        return ['iperf2', 'iperf3'].includes($scope.tool)
    }

    $scope.start_measurement = function() {
        console.log('hahaha');
    }

    $scope.show_measurement_button = function() {
        return true;
    }

});
