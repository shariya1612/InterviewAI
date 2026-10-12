document.addEventListener("DOMContentLoaded", function () {

    const answerBox = document.getElementById("answer");

    if (answerBox) {

        answerBox.addEventListener(
            "keydown",
            function (event) {

                if (
                    event.ctrlKey &&
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    if (this.form) {
                        this.form.submit();
                    }

                }

            }
        );

    }


    const numberChoices =
        document.querySelectorAll(
            ".number-choice label"
        );

    numberChoices.forEach(function (label) {

        const input =
            label.querySelector("input");

        if (!input) {
            return;
        }


        function update() {

            numberChoices.forEach(function (item) {
                item.classList.remove(
                    "selected-number"
                );
            });

            if (input.checked) {

                label.classList.add(
                    "selected-number"
                );

            }

        }


        input.addEventListener(
            "change",
            update
        );

        update();

    });

});