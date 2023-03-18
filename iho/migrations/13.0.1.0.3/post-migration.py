# Copyright 2021, Jarsa
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lpgl.html).

from odoo import tools

def migrate(cr, registry):
    """Import CSV data as it is faster than xml and because we can't use
    noupdate anymore with csv"""
    with tools.file_open("l10n_mx_edi/data/l10n_mx_edi.tariff.fraction.csv", "rb") as csv_file:
        cr.copy_expert(
            """COPY l10n_mx_edi_tariff_fraction(code, name, uom_code)
               FROM STDIN WITH DELIMITER '|'""", csv_file)
    # Create xml_id, to allow make reference to this data
    cr.execute(
        """UPDATE l10n_mx_edi_tariff_fraction
        SET active = 't'""")
    cr.execute(
        """INSERT INTO ir_model_data
           (name, res_id, module, model)
           SELECT concat('tariff_fraction_', code), id,
                'l10n_mx_edi_external_trade', 'l10n_mx_edi.tariff.fraction'
           FROM l10n_mx_edi_tariff_fraction """)
