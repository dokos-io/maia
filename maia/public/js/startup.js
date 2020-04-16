$(document).bind('startup', function() {
    if (has_common(frappe.user_roles, ["Administrator", "System Manager"])) {
        frappe.xcall("maia.maia.page.maia_account.maia_account.get_customer_payment_methods")
            .then(r => {
                if (r && r.message && r.message.data) {
                    const dates = r.message.data.map(f => new Date(f.card.exp_year, f.card.exp_month))
                    const max_date = moment(Math.max.apply(null, dates));
                    const diff = max_date > moment().add(-1, 'days') ? max_date.diff(moment().add(-1, 'days'), 'days') : null
                    if (diff && diff < 30) {
                        add_upgrade_bar(diff)
                    }
                }
            })
        }
})

const add_upgrade_bar = (days) => {

    const account_url = "href='/desk#maia-account' style='color: #608cff'"
    const plural_msg = __(`Your credit card expires in ${days} days. Please <a ${account_url}>update</a> your information.`)
    const single_msg = __(`Your credit card expires in ${days} day. Please <a ${account_url}>update</a> your information.`)

    $('footer').append(`
        <div class="upgrade-bar"
            style="bottom: 0px;
                position: fixed;
                background-color: #fffdf8;
                border: 1px solid #d1d8dd;
                z-index: 1;
                border-radius: 0;
                text-align: center;
                width: 100%;"
        >
            <div class="container">
                <p>${days > 1 ? plural_msg : single_msg}
                    <a type="button" class="dismiss-upgrade text-muted" data-dismiss="modal" aria-hidden="true"
                        style="position: absolute;
                        font-size: 20px;
                        top: 6px;
                        right: 15px;">
                        ×
                    </a>
                </p>
            </div>
        </div>
    `)

    $('.dismiss-upgrade').on('click', () => {
        $('.upgrade-bar').remove();
        localStorage.setItem("show_upgrade_bar", false);
    })
};