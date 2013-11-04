from osv import fields, osv
from datetime import datetime as dt
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
    
    def getSerials(self, cr, uid, context=None):
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
        return True
    
    
    _columns={
        'imei_selection' : fields.many2one('bsm.data', 'Select IMEI code', selection=_get_selection)
    }
    
bsm_importer()

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
    }

prodlot_bsm()