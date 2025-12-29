(function ($) {
    "use strict";

    $('body').on('click', '.js-generate-ai', function (e) {
        e.preventDefault();

        const $this = $(this);
        const type = $this.attr('data-type');
        const field = $this.attr('data-field');
        const title = $('input[name="title"]').val();

        if (title === '' || title === undefined) {
            alert('Please enter a course title first to provide context for AI.');
            return;
        }

        let question = "";
        if (type === 'summary') {
            question = "Generate a concise course summary for a course titled: " + title;
        } else if (type === 'description') {
            question = "Generate a detailed course description (HTML format) for a course titled: " + title;
        }

        $this.addClass('loading').prop('disabled', true);

        $.post('/panel/ai-contents/generate', {
            service_type: 'text',
            text_service_id: 'custom_text',
            question: question
        }, function (result) {
            $this.removeClass('loading').prop('disabled', false);

            if (result && result.code === 200 && result.data && result.data.contents && result.data.contents.length > 0) {
                const content = result.data.contents[0];

                if (field === 'summary') {
                    $('textarea[name="summary"]').val(content);
                } else if (field === 'description') {
                    const $textarea = $('textarea[name="description"]');
                    if ($textarea.length) {
                        $textarea.val(content);
                        // If summernote is used
                        if ($.fn.summernote) {
                            $textarea.summernote('code', content);
                        }
                    }
                }
            } else {
                alert('AI generation failed. Please check your API settings.');
            }
        }).fail(function (err) {
            $this.removeClass('loading').prop('disabled', false);
            alert('An error occurred during AI generation.');
            console.error(err);
        });
    });

})(jQuery);
