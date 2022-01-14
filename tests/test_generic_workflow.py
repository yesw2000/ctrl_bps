# This file is part of ctrl_bps.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import io
import unittest

import lsst.ctrl.bps.generic_workflow as gw
import networkx
import networkx.algorithms.isomorphism as iso


class TestGenericWorkflowJob(unittest.TestCase):
    def testEquality(self):
        job1 = gw.GenericWorkflowJob("job1")
        job2 = gw.GenericWorkflowJob("job1")
        self.assertEqual(job1, job2)


class TestGenericWorkflow(unittest.TestCase):
    def testAddJobDuplicate(self):
        job1 = gw.GenericWorkflowJob("job1")
        gwf = gw.GenericWorkflow("mytest")
        gwf.add_job(job1)
        with self.assertRaises(RuntimeError):
            gwf.add_job(job1)

    def testAddJobValid(self):
        job1 = gw.GenericWorkflowJob("job1")
        gwf = gw.GenericWorkflow("mytest")
        gwf.add_job(job1)
        self.assertEqual(1, gwf.number_of_nodes())
        self.assertListEqual(["job1"], list(gwf))
        getjob = gwf.get_job("job1")
        self.assertEqual(job1, getjob)

    def testAddJobRelationshipsSingle(self):
        job1 = gw.GenericWorkflowJob("job1")
        job2 = gw.GenericWorkflowJob("job2")
        gwf = gw.GenericWorkflow("mytest")
        gwf.add_job(job1)
        gwf.add_job(job2)
        gwf.add_job_relationships("job1", "job2")
        self.assertListEqual([("job1", "job2")], list(gwf.edges()))

    def testAddJobRelationshipsMultiChild(self):
        job1 = gw.GenericWorkflowJob("job1")
        job2 = gw.GenericWorkflowJob("job2")
        job3 = gw.GenericWorkflowJob("job3")
        gwf = gw.GenericWorkflow("mytest")
        gwf.add_job(job1)
        gwf.add_job(job2)
        gwf.add_job(job3)
        gwf.add_job_relationships("job1", ["job2", "job3"])
        self.assertListEqual([("job1", "job2"), ("job1", "job3")], list(gwf.edges()))

    def testAddJobRelationshipsMultiParents(self):
        job1 = gw.GenericWorkflowJob("job1")
        job2 = gw.GenericWorkflowJob("job2")
        job3 = gw.GenericWorkflowJob("job3")
        gwf = gw.GenericWorkflow("mytest")
        gwf.add_job(job1)
        gwf.add_job(job2)
        gwf.add_job(job3)
        gwf.add_job_relationships(["job1", "job2"], "job3")
        self.assertListEqual([("job1", "job3"), ("job2", "job3")], list(gwf.edges()))

    def testAddJobRelationshipsNone(self):
        job1 = gw.GenericWorkflowJob("job1")
        gwf = gw.GenericWorkflow("mytest")
        gwf.add_job(job1)
        gwf.add_job_relationships(None, "job1")
        self.assertListEqual([], list(gwf.edges()))
        gwf.add_job_relationships("job1", None)
        self.assertListEqual([], list(gwf.edges()))

    def testGetJobExists(self):
        job1 = gw.GenericWorkflowJob("job1")
        gwf = gw.GenericWorkflow("mytest")
        gwf.add_job(job1)
        job2 = gwf.get_job("job1")
        self.assertIs(job1, job2)

    def testGetJobError(self):
        job1 = gw.GenericWorkflowJob("job1")
        gwf = gw.GenericWorkflow("mytest")
        gwf.add_job(job1)
        with self.assertRaises(KeyError):
            _ = gwf.get_job("job_not_there")

    def testSaveInvalidFormat(self):
        gwf = gw.GenericWorkflow("mytest")
        stream = io.BytesIO()
        with self.assertRaises(RuntimeError):
            gwf.save(stream, "badformat")

    def testSavePickle(self):
        gwf = gw.GenericWorkflow("mytest")
        job1 = gw.GenericWorkflowJob("job1")
        job2 = gw.GenericWorkflowJob("job2")
        gwf.add_job(job1)
        gwf.add_job(job2)
        gwf.add_job_relationships("job1", "job2")
        stream = io.BytesIO()
        gwf.save(stream, "pickle")
        stream.seek(0)
        gwf2 = gw.GenericWorkflow.load(stream, "pickle")
        self.assertTrue(
            networkx.is_isomorphic(gwf, gwf2, node_match=iso.categorical_node_match("data", None))
        )


if __name__ == "__main__":
    unittest.main()
