from odoo import models, fields, api
from datetime import datetime
from odoo.exceptions import AccessError, UserError, ValidationError


class CustomHrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'


    def compute_sheet(self):
        rec = super(CustomHrPayslip, self).compute_sheet()
        for record in self:
            if record.struct_id.contract_id.structure == True:
                if record.struct_id.type_id.id == record.contract_id.structure_type_id.id:
                    salary_rule = self.env['hr.salary.rule']
                    rule_line_all = salary_rule.search([('struct_id','=', record.struct_id.id)])
                    rule_line = rule_line_all.search([('start_date','<=', record.date_from),('end_date', '>=', record.date_to)])                                                         #,('start_date','<=', record.date_from),('end_date','>',record.date_from),('start_date','<',record.date_to),('end_date', '>=',record.date_to)])
                    rule = rule_line_all - rule_line
                    payslip_line = self.env['hr.payslip.line']
                    slip_line = payslip_line.search([('slip_id', '=', record.id),('salary_rule_id','in',rule.ids)])
                    slip_line.unlink()
                    return rec
                else:
                    raise ValidationError("the structure not have this contract")
                


class HrPayrollStructure(models.Model):
    _name = 'hr.payroll.structure'
    _inherit = 'hr.payroll.structure'

    contract_id = fields.Many2one('hr.contract')

    @api.model
    def create(self, vals):
        rec = super(HrPayrollStructure, self).create(vals)
        if vals['contract_id'] != False:
            rule_obj = rec.rule_ids.search([('struct_id','=', rec.id)])
            if rule_obj:
                for rule in rule_obj:
                    rule.write({'start_date':rec[0].contract_id.date_start}) 
                    rule.write({'end_date':rec[0].contract_id.date_end })
        return rec



class HrContract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    structure = fields.Boolean('New Structure')


    @api.model
    def create(self, vals):
        rec = super(HrContract, self).create(vals)
        if vals['structure'] == True:
            payroll_structure_obj = self.env['hr.payroll.structure']
            if  vals['structure_type_id'] and vals['employee_id']:
                payroll_structure = {
                    'name': vals['name'] ,
                    'type_id': vals['structure_type_id'] ,
                    'country_id':'',
                    'journal_id': '',
                    'contract_id': rec.id,
                    'use_worked_day_lines': True
                }
                payroll_structure_obj.create(payroll_structure)
        return rec

    # def write(self, vals):
    #     rec = super(HrContract, self).write(vals)
    #     payroll_structure_obj = self.env['hr.payroll.structure']
    #     payroll_structure_list= payroll_structure_obj.search([('contract_id','=', self.id)])
    #     if len(payroll_structure_list)>0:
    #         payroll_structure_list[0].write({'type_id':self.structure_type_id.id})
    #         for rule in payroll_structure_list[0].rule_ids:
    #             rule.write({'start_date': self.date_start})
    #             rule.write({'end_date': self.date_end})
    #     return rec





