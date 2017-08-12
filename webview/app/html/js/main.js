var application = function(){

 
RobotUtils.subscribeToALMemoryEvent("FrontTactilTouched", function(value) {
  alert("Head touched: " + value);
});

RobotUtils.subscribeToALMemoryEvent("StartGame", function(value) {
  alert("Start Game: " + value);
});

 




    RobotUtils.onServices(function(ALLeds, ALTextToSpeech) {
        ALLeds.randomEyes(2.0);
         ALTextToSpeech.say("1, Click on the box that has a different color compared to the others");
       //  ALTextToSpeech.say("2, The test begins when you click on the first box");
        // ALTextToSpeech.say("3, You have 15 seconds to decide on each panel");
      //  ALTextToSpeech.say("4, If you click on the wrong box, you will lose 3 seconds");
      });


     
    RobotUtils.onService(function (VisionTeraphyService) {
        $("#noservice").hide();
        VisionTeraphyService.get().then(function(level) {
            // Find the button with the right level:
            $(".levelbutton").each(function() {
                var button = $(this);
                if (button.data("level") == level) {
                    button.addClass("highlighted");
                    button.addClass("clicked");
                }
            });
			 $(".Startbutton").click(function() {
               RobotUtils.onServices(function(ALMemory) {
					ALMemory.raiseEvent("StartGame", "data");
				}); 
            });
            // ... and show all buttons:
            $("#buttons").show();
        });
        $(".levelbutton").click(function() {
            // grey out the button, until we hear back that the click worked.
            var button = $(this);
            var level = button.data("level");
            $(".levelbutton").removeClass("highlighted");
            $(".levelbutton").removeClass("clicked");
            button.addClass("clicked");
            VisionTeraphyService.set(level).then(function(){
                button.addClass("highlighted");
            });
        })
    }, function() {
        console.log("Failed to get the service.")
        $("#noservice").show();
    });
};
