var myApp = angular.module('psApp', []);

myApp.controller('sls', function($scope, $http) {

    $scope.mplist = [];
    $scope.full_mplist = [];
    $scope.communities = [];
    $scope.community = "";
    $scope.tools = [];
    $scope.tool = "";

    $scope.source = "";
    $scope.destination = "";

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


});
