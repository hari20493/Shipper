$(function () {
    $('.details_btn').click(function () {
        $('.content').css('display', 'none');
        $('.loader').addClass('d-flex');
        $('#shipment_id').text('');
        $('#weight').text('');
        $('#company_name').text('');
        $('.pending').addClass('badge-info');
        $('.sending').addClass('badge-info');
        $('.received').addClass('badge-info');
        $('.pending').removeClass('badge-success');
        $('.sending').removeClass('badge-success');
        $('.received').removeClass('badge-success');
        let shipment_id = $(this).data('shipment-id');
        $.ajax({
            url: '/dashboard/shipment-details/' + shipment_id,
            type: 'GET',
            success: function (data) {
                $('.loader').removeClass('d-flex');
                $('.content').css('display', 'block');
                $('#shipment_id').text(data.shipping_code);
                $('#weight').text(data.weight);
                $('#company_name').text(data.customer);
                $('.' + data.shipment_current_status).removeClass('badge-info');
                $('.' + data.shipment_current_status).addClass('badge-success');
                $('#status').removeClass('badge-info');
                $('#status').addClass('badge-success');
                $('#status').text(data.shipment_current_status);
                $('#updated').text(data.last_updated_date);
            }
        });
    });

})

function changeStatus(status) {
    let shipment_id = $('#shipment_id').text();
    $('.spinner-' + status).css('display', 'inline-block');
    $('.pending').addClass('badge-info');
    $('.sending').addClass('badge-info');
    $('.received').addClass('badge-info');
    $.ajax({
        url: '/dashboard/change-status/' + shipment_id + '/' + status,
        type: 'GET',
        success: function (data) {
            $('.spinner-' + status).css('display', 'none');
            $('.' + data.status).removeClass('badge-info');
            $('.' + data.status).addClass('badge-success');
        }
    });
}