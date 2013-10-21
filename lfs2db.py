from osv import fields, osv

class bsm_importer(osv.osv_memory):

    LOCALFILEPATH = '/home/parallels/bsm/bsm.txt'
    
    _name='bsm.importer'
    #_inherit='mrp.product.produce'
    
    _columns={
        'imei_selection' : fields.many2one('bsm.data', 'Select IMEI code', selection=_get_selection)
    }
    
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
        try:
            f = open(LOCALFILEPATH, 'r')
            for line in f.readline():
                print 'line: ' + str(line)
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
        except:
            print 'lol random error'
        
        return True
    

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
        # TODO needs a relative field pointing to lot serials?
    }
    
bsm_data()
    