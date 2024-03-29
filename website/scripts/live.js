$(document).ready(function() {
    const server = "https://flyyrin.pythonanywhere.com/game"
    var currentData = []
    const colors = {
        "c" : "#4de1ff",
        "h" : "#ffffff",
        "p" : "#eba152",
        "e": "#00000000",
        "red": "#fc4c4f",
        "blue": "#4fa3fc",
        "yellow": "#ECD13F",
        "green": "#4bec3f",
        "purple": "#cf3fec",
        "king-red": "#ff0004",
        "king-blue": "#007bff",
        "king-yellow": "#d6b500",
        "king-green": "#0cad00",
        "king-purple": "#a200c3",
    }

    function update() {
        $.get(server, function(data) {
            data = JSON.parse(data);
            
            var newData = [data.gameData.np1, data.gameData.np2, data.gameData.cp1, data.gameData.cp2]
            if (newData != currentData) {
                currentData = newData
                $(".player1").attr('class', 'playertag player1');
                $(".player2").attr('class', 'playertag player2');
                $(".player1").html(data.gameData.np1)
                $(".player2").html(data.gameData.np2)
                $(".player1").addClass(data.gameData.cp1+"-text")
                $(".player2").addClass(data.gameData.cp2+"-text") 
            }

            if (!data.game && !data.winner) {
                $("#noGameModal").modal('show');
            } else if (!data.game && data.winner) {
                $("#noGameModal").modal('hide');
                $(".winner").attr('class', 'winner black-text-shadow');
                if (data.winner == 1) {
                    $(".winner").text(data.gameData.np1);
                    $(".winner").addClass(data.gameData.cp1+"-text");
                }
                if (data.winner == 2) {
                    $(".winner").text(data.gameData.np2);
                    $(".winner").addClass(data.gameData.cp2+"-text");
                }
                $("#winnerModal").modal('show');
            } else {
                $("#noGameModal").modal('hide');
                $("#winnerModal").modal('hide');
                var startTime = new Date(data.gameData.startTime)
                var currentTime = new Date(data.gameData.currentTime);
                var alphaSeconds = (currentTime.getTime() - startTime.getTime())/1000
                var mmss = new Date(alphaSeconds * 1000).toISOString().substring(14, 19)
                $(".timer").html(mmss)

                if (data.gameData.playing == 1) {
                    $(".player1").addClass("playing")
                    $(".player2").removeClass("playing")
                }
                if (data.gameData.playing == 2) {
                    $(".player2").addClass("playing")
                    $(".player1").removeClass("playing")
                }

                $(".player1-pieces").html($(".player1-pieces").html().split(":")[0] + ": " + data.gameData.pieces.player1.pieces)
                $(".player1-kings").html($(".player1-kings").html().split(":")[0] + ": " +  data.gameData.pieces.player1.kings)
                $(".player1-captured").html($(".player1-captured").html().split(":")[0] + ": " + data.gameData.pieces.player1.captured)
                $(".player2-pieces").html($(".player2-pieces").html().split(":")[0] + ": " + data.gameData.pieces.player2.pieces)
                $(".player2-kings").html($(".player2-kings").html().split(":")[0] + ": " +  data.gameData.pieces.player2.kings)
                $(".player2-captured").html($(".player2-captured").html().split(":")[0] + ": " + data.gameData.pieces.player2.captured)

                $.each(data.gameData.board, function(position, piece) {
                    if (piece == 1) {
                        $(`.board > svg > #${position}`).attr("fill", colors[data.gameData.cp1]);
                    }
                    if (piece == 3) {
                        $(`.board > svg > #${position}`).attr("fill", colors[`king-${data.gameData.cp1}`]);
                    }
                    if (piece == 2) {
                        $(`.board > svg > #${position}`).attr("fill", colors[data.gameData.cp2]);
                    }
                    if (piece == 4) {
                        $(`.board > svg > #${position}`).attr("fill", colors[`king-${data.gameData.cp2}`]);
                    }
                    if (piece == "e") {
                        $(`.board > svg > #${position}`).attr("fill", colors[piece]);
                    }
                    if (piece == "c") {
                        $(`.board > svg > #${position}`).attr("fill", colors[piece]);
                    }
                    if (piece == "h") {
                        $(`.board > svg > #${position}`).attr("fill", colors[piece]);
                    }
                    if (piece == "p") {
                        $(`.board > svg > #${position}`).attr("fill", colors[piece]);
                    }
                });
            }
        });
    }

    if ($(window).width() < 960) {
        $(".board").load("images/m-board.svg")
        $(".pieces").removeClass("d-flex")
        $(".pieces").hide();
    } else {
        $(".board").load("images/board.svg")
    }

    update()
    setInterval(function() {
        update();
    }, 50);
})