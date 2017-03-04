var activity_charts = require("./activity_charts");
var assert = require('assert');

describe('Array', function() {
  describe('min_max)', function() {
    
    var empty_array = min_max([]);

    it('should return [None, None] array when the array is not present', function() {
      assert.equal([None, None], empty_array);
    });
  });
});
