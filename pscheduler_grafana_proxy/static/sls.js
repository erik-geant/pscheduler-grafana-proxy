var myApp = angular.module('psApp', []);

myApp.controller('sls', function($scope, $http) {

    $scope.mplist = [];
    $scope.status = 'not yet loaded';

    $http({
        method: 'GET',
        url: window.location.origin + "/sls/mplist/owping"
    }).then(
        function(rsp) {
            $scope.mplist = rsp.data;
        },
        function(rsp) {
            $scope.mplist = ['error'];
        }


    );

});
