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
        print '_select_bsm_rows'
        obj = self.pool.get('bsm.data')
        ids = obj.search(cr, uid, [])
        #args=[('bsm_used', '=', False)
        print 'found unused bsm numbers: ' + str(ids)
        res = obj.read(cr, uid, ids, ['id', 'bsm_imei_code', 'bsm_product_code'], context)
        print str(res)
        res = [(r['id'], r['bsm_imei_code']) for r in res]
        print str(res)
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
        print 'select_bsm_on_change'

        value = {}
        if bsm_id:
            #bsm_ids = self.pool.get('bsm.data').search(cr, uid, [('id', '=', bsm_id)])
            print 'context: ' + str(context)
            print 'selected: ' + str(bsm_id)
            self.selectedId = bsm_id
        return True
    
    _columns = {
        'bsm_id': fields.many2one('bsm.data', 'Select BSM', selection=_select_bsm_rows) #, domain="[('bsm_used','=','False')]"
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
class bsm_importer(osv.osv_memory):

    LOCALFILEPATH = '/home/parallels/bsm/bsm.txt'
    
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
        '''
        try:
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
        except IOError as ioe:
            print "I/O error({0}): {1}".format(ioe.errno, ioe.strerror)
        except ValueError as fe:
            print fe.strerror
        except:
            print 'lol random error'
        '''
        raise osv.except_osv('BSM', 'No files found')
        return True
    
    
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

    _columns={
        'imei_selection' : fields.many2one('bsm.data', 'Select IMEI code', selection=_get_selection)
    }
    
bsm_importer()

