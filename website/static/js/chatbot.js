/*This script handles chatbox animation*/
$(document).ready(function () {
    $(".chatbox").each(function () {
        var $chatbox = $(this);

        $chatbox.find(".sendmessage input").focus(function () {
            if ($(this).val() == "Send message...") {
                $(this).val("");
            }
        });

        $chatbox.find(".sendmessage input").focusout(function () {
            if ($(this).val() == "") {
                $(this).val("Send message...");
            }
        });

        $chatbox.find(".sendButton").click(function () {
            var message = $chatbox.find(".messageInput").val();
            var chatboxId = $chatbox.attr("id");
            var selectedModel = $chatbox.find(".friend.selectedFriend").find("p strong").html();

            // Create an object to hold the data
            var data = {
                message: message,
                chatboxId: chatboxId,
                selectedModel: selectedModel
            };

            // Make the AJAX request to the Flask server
            $.ajax({
                type: "POST",
                url: "/send_message",
                data: data,    
                beforeSend: function() {
                    // Perform actions before the AJAX request is sent
                    // For example, show a loading indicator
                    var chatboxSelector = '#' + chatboxId + ' .chat-messages .msgs';  // Select the specific chat-messages instance
                    $(chatboxSelector).append('<div class="message"><img src="../static/resources/'+selectedModel+'.png"><div class="bubble">...</div></div>');
                },
                success: function (response) {
                    if ('messages' in response) {
                        var chatMessagesHTML = response['messages'];
                        var chatboxSelector = '#' + chatboxId + ' .chat-messages .msgs';  // Select the specific chat-messages instance
                        $(chatboxSelector).html(chatMessagesHTML);
                        
                    } else {
                        console.log("Error: No messages in the response");
                    }
                    // Set the .messageInput value to an empty string
                },
                error: function (xhr, status, error) {
                    // Handle any errors that occur during the AJAX request
                    console.log("AJAX request failed");
                    console.log(error);
                },
                complete: function() {
                    // This block will be executed after success or error, i.e., after the AJAX request completes
                    $chatbox.find(".messageInput").val('');
                }
            });
        });


        $chatbox.find(".friend").each(function () {
            $(this).click(function () {
                var childOffset = $(this).offset();
                var parentOffset = $(this).parent().parent().offset();
                var childTop = childOffset.top - parentOffset.top;
                var clone = $(this).find("img").eq(0).clone();
                var top = childTop + 12 + "px";

                // Add the "selectedFriend" class to the clicked ".friend" component
                $(this).addClass("selectedFriend");
                
                $(clone)
                    .css({ top: top })
                    .addClass("floatingImg")
                    .appendTo($chatbox.find(".chat-messages"));

                setTimeout(function () {
                    $chatbox.find(".profile p").addClass("animate");
                    $chatbox.find(".profile").addClass("animate");
                }, 100);

                setTimeout(function () {
                    $chatbox.find(".chat-messages").addClass("animate");
                    $chatbox.find(".cx, .cy").addClass("s1");
                    setTimeout(function () {
                        $chatbox.find(".cx, .cy").addClass("s2");
                    }, 100);
                    setTimeout(function () {
                        $chatbox.find(".cx, .cy").addClass("s3");
                    }, 200);
                }, 150);

                $chatbox.find(".floatingImg").animate(
                    {
                        /*'width': "68px",*/
                        left: "45%",
                        top: "2%",
                    },
                    200
                );

                var name = $(this).find("p strong").html();
                $chatbox.find(".profile p").html(name);

                $chatbox
                    .find(".message")
                    .not(".right")
                    .find("img")
                    .attr("src", $(clone).attr("src"));
                $chatbox.find(".friendslist").fadeOut();
                $chatbox.find(".chatview").fadeIn();

                $chatbox.find(".close").unbind("click").click(function () {
                    // Remove the "selectedFriend" class from the associated ".friend" component
                    $chatbox.find(".friend.selectedFriend").removeClass("selectedFriend");

                    $chatbox.find(".chat-messages, .profile, .profile p").removeClass("animate");
                    $chatbox.find(".cx, .cy").removeClass("s1 s2 s3");
                    $chatbox.find(".floatingImg").animate(
                        {
                            width: "40px",
                            top: top,
                            left: "12px",
                        },
                        200,
                        function () {
                            $chatbox.find(".floatingImg").remove();
                        }
                    );

                    setTimeout(function () {
                        $chatbox.find(".chatview").fadeOut();
                        $chatbox.find(".friendslist").fadeIn();
                    }, 50);
                });

                var name = $(this).find("p strong").html();
                var chatboxId = $chatbox.attr("id");
                // Send the value to the Flask server using an AJAX request

                // Create an object to hold the data
                var data = {
                    name: name,
                    chatboxId: chatboxId
                };
                // Make the AJAX request to the Flask server
                $.ajax({
                    type: "POST",
                    url: "/friend_selected",
                    data: data,
                    success: function (response) {
                        // Handle the response from the Flask server
                        if ('messages' in response) {
                            var chatMessagesHTML = response['messages'];
                            var chatboxSelector = '#' + chatboxId + ' .chat-messages .msgs';  // Select the specific chat-messages instance
                            $(chatboxSelector).html(chatMessagesHTML);
                        } else {
                            console.log("Error: No messages in the response");
                        }

                    },
                    error: function (xhr, status, error) {
                        // Handle any errors that occur during the AJAX request
                        console.log("AJAX request failed");
                        console.log(error);
                    }
                });
            });
        });
    });
});