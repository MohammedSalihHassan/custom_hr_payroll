from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError

class HrSalaryRule(models.Model):
    _name = 'hr.salary.rule'
    _inherit = 'hr.salary.rule'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    rule_account_line_ids = fields.One2many('rule.account.line', 'salary_rule_id', string='Account Line')

    @api.constrains('start_date','end_date')
    def _check_date(self):
        for record in self:
            if record.start_date and record.end_date:
                if record.start_date >= record.end_date:
                    raise ValidationError("Start Date > End Date ccc -in- salary rule")
        
    @api.constrains('rule_account_line_ids')
    def _check_avg(self):
        for record in self:
            if self.rule_account_line_ids:
                credit_avg = sum(self.rule_account_line_ids.mapped('credit_avg'))
                debit_avg = sum(self.rule_account_line_ids.mapped('debit_avg'))
                if debit_avg > 100 or credit_avg > 100:
                    raise ValidationError("Total avg is 100")


class CustomHrPayslip(models.Model):
    _inherit = 'hr.payslip'



    def _prepare_slip_lines(self, date, line_ids):
        rec = super(CustomHrPayslip, self)._prepare_slip_lines(date, line_ids)

        return rec
        

class HrRuleAccountLine(models.Model):
    _name = 'rule.account.line' 

    account_debit = fields.Many2one('account.account', 'Debit Account', company_dependent=True, domain=[('deprecated', '=', False)])
    debit_avg = fields.Integer('Debit %', group_operator='avg')
    account_credit = fields.Many2one('account.account', 'Credit Account', company_dependent=True, domain=[('deprecated', '=', False)])
    credit_avg = fields.Integer('Credit %', group_operator='avg')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', company_dependent=True)
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Salary Rule', required= True)


    @api.constrains('debit_avg','credit_avg')
    def _check_avg(self):
        for record in self:
            if record.debit_avg or record.credit_avg:
                if record.debit_avg > 100 or record.credit_avg > 100 or record.debit_avg < 0 or record.credit_avg <0:
                    raise ValidationError('debit avg and credit avg > 100 or < 0')