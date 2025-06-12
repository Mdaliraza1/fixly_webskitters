(function($) {
    $(document).ready(function() {
        $('#id_service').change(function() {
            const selectedServiceId = $(this).val();
            const baseUrl = window.location.href.split('?')[0];
            window.location.href = `${baseUrl}?service=${selectedServiceId}`;
        });
    });
})(django.jQuery);
