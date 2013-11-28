from osv import fields, osv
from datetime import datetime as dt

'''
Class for holding the data
'''
class bsm_data(osv.osv_memory):
    _name = 'bsm.data'
    
    _columns={
        'bsm_imei_code': fields.char('IMEI Code', size=15),
        'bsm_product_code': fields.char('Product code', size=64),
        'bsm_date': fields.datetime('Import date'),
        'bsm_used': fields.boolean('Used')
        # TODO needs a relative field pointing to lot serials?
    }
    
    _defaults = {
        'bsm_used': False
    }
    
bsm_data()

class prodlot_bsm(osv.osv_memory):
    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'

    _columns = {
        'bsm_id': fields.many2one('bsm.data', 'BSM data', select=True),
        'bsm_imei_code': fields.related('bsm_id','bsm_imei_code',type='char', relation="bsm.data", string="IMEI"),
        'bsm_product_code': fields.related('bsm_id','bsm_product_code',type='char', relation="bsm.data", string="Product code")
    }

prodlot_bsm()


class stock_move_split_bsm(osv.osv_memory):
    _name = 'stock.move.split'
    _inherit = 'stock.move.split'
    
    selectedId = ""
    
    def _select_bsm_rows(self, cr, uid, context=None):
        print '_get_selection'
        obj = self.pool.get('bsm.data')
        
        unused = obj.search(cr, uid, args=[('bsm_used', '=', False)], context=context)
        
        data = obj.read(cr, uid, unused,['id', 'bsm_imei_code', 'bsm_product_code'], context=context)
        res = ()
        if len(data) > 0:
            # return list of tuples
            res = [(r['id'], r['bsm_imei_code']+','+r['bsm_product_code']) for r in data]
        return res
    
    def split_lot(self, cr, uid, ids, context=None):
        print 'bsm split_lot'
        print str(context)
        # Call super class 
        super(stock_move_split_bsm, self).split_lot(cr, uid, ids, context=context)

        print 'selected id: ' + str(self.selectedId)
        if self.selectedId != "":
            moves = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context)
            bsm = self.pool.get('bsm.data').browse(cr, uid, self.selectedId, context)
            print str(moves)
            if moves and bsm:
                prodlot_obj = self.pool.get('stock.production.lot')
                print 'saving bsm id ' + str(self.selectedId) + ' to prodlot ' + str(moves.prodlot_id.id)
                prodlot_obj.write(cr, uid, moves.prodlot_id.id, {'bsm_id': bsm.id})
                self.pool.get('bsm.data').write(cr, uid, bsm.id, {'bsm_used': True})
        return True
    
    def selected_bsm_on_change(self, cr, uid, ids, bsm_id, context=None):
        print 'select_bsm_on_change ' + str(bsm_id)
        value = {}
        if bsm_id:
            self.selectedId = bsm_id
        return True
    
    _columns = {
        'bsm_id': fields.selection(_select_bsm_rows, 'Select BSM') #, domain="[('bsm_used','=','False')]"
    }

stock_move_split_bsm()

class stock_move_bsm(osv.osv_memory):
    _name = 'stock.move'
    _inherit = 'stock.move'

    _columns = {
        'bsm_imei_code': fields.related('prodlot_id','bsm_id', 'bsm_imei_code', type='char', relation="bsm.data", string="IMEI", readonly=True),
        'bsm_product_code': fields.related('prodlot_id','bsm_id', 'bsm_product_code', type='char', relation="bsm.data", string="Product", readonly=True)
    }

stock_move_bsm()

'''
BSM file importer UI methods and data deserialization
'''
import os
import csv

class bsm_importer(osv.osv_memory):

    LOCALFILEPATH = '/home/parallels/bsm/'
    
    _name='bsm.importer'
    #_inherit='mrp.product.produce'
    
    def _get_selection(self, cr, uid, context=None):
        print 'bsm.importer._get_selection'
        obj = self.pool.get('bsm.data')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['bsm_imei_code', 'bsm_product_code'], context)
        res = [(r['bsm_product_code'], r['bsm_imei_code']) for r in res]
        return res
    
    def getSerials(self, cr, uid, ids, context=None):
        print 'getSerials()'
        # Read local file from the file system
        obj = self.pool.get('bsm.importer')
        filepath = obj.browse(cr, uid, ids, context=context)[0].filepath
        created = 0
        try:
            if filepath == "":
                os.chdir(self.LOCALFILEPATH)
            else:
                os.chdir(filepath)
                
            for files in os.listdir("."):
                if files.endswith(".bsm"):
                    print 'opening file ' + files
                    with open(files, 'rb') as csvfile:
                        hasHeader = True
                        bsm_obj = self.pool.get('bsm.data')
                        header = []
                        reader = csv.reader(csvfile, delimiter=',')
                        
                        for row in reader:
                            if reader.line_num == 1 and hasHeader:
                                print 'header found'
                                header = row
                            else:
                                # search for existing bsm
                                existing = bsm_obj.search(cr, uid, args=[('bsm_imei_code', '=', row[0])])
                                if len(existing) == 0 and len(row) > 1:
                                    # create a new bsm
                                    bsm_obj.create(cr, uid, vals={'bsm_imei_code': row[0], 'bsm_product_code': row[1]})
                                    created += 1

                        print 'created ' + str(created) + ' bsm rows'
                        csvfile.close()
                    
            '''       
            f = open(self.LOCALFILEPATH, 'r')
            for line in f:
                if line is not '' and line[0] is not '#':
                    params = line.split(';')
                    if len(params) == 3:
                        # read date
                        vals = {
                            'bsm_date': dt.strptime(params[0], "%d-%m-%Y %H:%M.%S")
                            'bsm_imei_code': params[1]
                            'bsm_product_code': params[2]
                        }
                        
                        # create object
                        bsm_obj = self.pool.get('bsm.data')
                        existing = bsm_obj.search(cr, uid, [('bsm_imei_code','=',vals['bsm_imei_code'])], context=context)
                        if len(existing) == 0:
                            print 'Creating BSM serial'
                            new_device = bsm_obj.create(cr, uid, vals, context=context)
                        else:
                            print 'IMEI code exists already'
                    else:
                        raise ValueError("Line format not recognized")
            f.close()
            ''' 
        except IOError as ioe:
            print "I/O error({0}): {1}".format(ioe.errno, ioe.strerror)
        except ValueError as fe:
            print fe.strerror
        except:
            print 'lol random error'
        
        return self.pool.get('warning').info(cr, uid, title='BSM', message="%s BSM rows created "%(str(created)))
    
    
    def addBSM(self, cr, uid, context=None):
        print 'addBSM'
        
        return {
            'view_id': 'bsm_data_view',
            'views': 'form',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'bsm.data',
            #'res_id': prod.move_created_ids2[len(prod.move_created_ids2)-1].id,
            'view_mode': 'form',
            'target': 'new',
            'context': context,
       }

    def _get_bsm_data(self, cr, uid, name, ids, context=None):
        print 'get bsm data'
        obj = self.pool.get('bsm.data')
        
    def _get_selection(self, cr, uid, context=None):
        print '_get_selection'
        obj = self.pool.get('bsm.data')
        
        unused = obj.search(cr, uid, args=[('bsm_used', '=', False)], context=context)
        
        data = obj.read(cr, uid, unused,['id', 'bsm_imei_code', 'bsm_product_code'], context=context)
        res = ()
        if len(data) > 0:
            # return list of tuples
            res = [(r['id'], r['bsm_imei_code']+','+r['bsm_product_code']) for r in data]
        return res
        
    _columns={
        'imei_selection' : fields.many2one('bsm.data', 'Select IMEI code'),#, selection=_get_selection)
        'imeis_name': fields.selection(_get_selection,'Unused IMEI codes'), 
        'filepath': fields.char('BSM Filepath', required=False)
    }
    
    _defaults={
        'filepath': '/home/bsm/',
    }
    
bsm_importer()

