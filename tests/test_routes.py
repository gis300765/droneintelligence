import unittest
from backend.server import app
class Routes(unittest.TestCase):
    def setUp(self):self.client=app.test_client()
    def get(self,*args,**kwargs):
        response=self.client.get(*args,**kwargs)
        self.addCleanup(response.close)
        return response
    def test_landing(self):
        r=self.get('/')
        self.assertEqual(r.status_code,200)
        self.assertIn(b'droneintelligence',r.data)
        self.assertIn(b'/app/?',r.data)
    def test_platform_and_configuration(self):
        r=self.get('/app/')
        self.assertEqual(r.status_code,200)
        self.assertIn(b'DRONEINTELLIGENCE_API_BASE',r.data)
        self.assertEqual(self.get('/config.js').status_code,200)
    def test_health_without_private_data(self):
        self.assertTrue(self.get('/api/health').json['geotiff'])
        self.assertEqual(self.get('/api/library').json,[])
    def test_unknown_raster_is_not_read(self):
        self.assertEqual(self.get('/api/rasters/not-registered/tile/1/0/0.png').status_code,404)
    def test_local_host_restriction(self):
        self.assertEqual(self.get('/',headers={'Host':'example.invalid'}).status_code,403)
    def test_assets(self):
        for filename in ['project-1.webp','inter.ttf','OFL-Inter.txt']:
            self.assertEqual(self.get('/landing-assets/'+filename).status_code,200)
if __name__=='__main__':unittest.main()
